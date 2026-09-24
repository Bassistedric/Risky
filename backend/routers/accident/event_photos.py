# ============================================================
# RISKY — ROUTER PHOTOS ÉVÉNEMENT
# ============================================================

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Response,
    UploadFile,
)

from ...database import SessionLocal
from ...schemas.event_photos import (
    EventPhotoListResponse,
    EventPhotoResponse,
    EventPhotoUpdate,
)
from ...services.audit import write_audit_log
from ...services.event_photos import (
    MAX_PHOTOS_PER_EVENT,
    STORAGE_ROOT,
    create_event_photo,
    delete_event_photo,
    get_event_photos,
    update_event_photo,
)
from ...services.session import require_write_session


router = APIRouter(
    prefix="/events",
    tags=["Event Photos"],
)


# ============================================================
# LISTE DES PHOTOS
# ============================================================

@router.get(
    "/{event_id}/photos",
    response_model=EventPhotoListResponse,
)
def list_event_photos(
    event_id: int,
):
    db = SessionLocal()

    try:
        photos = get_event_photos(
            db=db,
            event_id=event_id,
        )

        return EventPhotoListResponse(
            event_id=event_id,
            photos=photos,
            count=len(photos),
            max_photos=MAX_PHOTOS_PER_EVENT,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    finally:
        db.close()


# ============================================================
# AJOUT D'UNE PHOTO
# ============================================================

@router.post(
    "/{event_id}/photos",
    response_model=EventPhotoResponse,
)
async def upload_event_photo(
    event_id: int,
    file: UploadFile = File(...),
    session=Depends(require_write_session),
):
    db = SessionLocal()
    created_file_path = None

    try:
        content = await file.read()

        photo = create_event_photo(
            db=db,
            event_id=event_id,
            original_filename=file.filename or "photo",
            content_type=file.content_type or "",
            content=content,
            uploaded_by_person_id=session["person_id"],
        )
        storage_root = STORAGE_ROOT.parent.parent
        created_file_path = storage_root / photo.storage_path

        write_audit_log(
            db=db,
            session=session,
            action="CREATE",
            entity_type="EVENT_PHOTO",
            entity_id=photo.id,
            after_data={
                "event_id": photo.event_id,
                "original_filename": photo.original_filename,
                "content_type": photo.content_type,
                "file_size": photo.file_size,
                "sort_order": photo.sort_order,
            },
            details="Ajout d'une photo au dossier événement.",
        )

        db.commit()
        db.refresh(photo)

        return photo

    except ValueError as exc:
        db.rollback()

        if created_file_path is not None and created_file_path.exists():
            created_file_path.unlink()

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception:
        db.rollback()

        if created_file_path is not None and created_file_path.exists():
            created_file_path.unlink()

        raise

    finally:
        db.close()

        # ============================================================
# AFFICHAGE D'UNE PHOTO
# ============================================================

@router.get(
    "/{event_id}/photos/{photo_id}/file",
)
def get_event_photo_file(
    event_id: int,
    photo_id: int,
):
    db = SessionLocal()

    try:
        photos = get_event_photos(
            db=db,
            event_id=event_id,
        )

        photo = next(
            (
                item
                for item in photos
                if item.id == photo_id
            ),
            None,
        )

        if photo is None:
            raise HTTPException(
                status_code=404,
                detail="Photo introuvable.",
            )

        storage_root = STORAGE_ROOT.parent.parent
        file_path = storage_root / photo.storage_path

        if not file_path.exists():
            raise HTTPException(
                status_code=404,
                detail="Fichier photo introuvable.",
            )

        return Response(
            content=file_path.read_bytes(),
            media_type=photo.content_type,
        )

    finally:
        db.close()


# ============================================================
# LÉGENDE / ORDRE
# ============================================================

@router.put(
    "/{event_id}/photos/{photo_id}",
    response_model=EventPhotoResponse,
)
def modify_event_photo(
    event_id: int,
    photo_id: int,
    payload: EventPhotoUpdate,
    session=Depends(require_write_session),
):
    db = SessionLocal()

    try:
        photo = update_event_photo(
            db=db,
            event_id=event_id,
            photo_id=photo_id,
            caption=payload.caption,
            sort_order=payload.sort_order,
        )

        write_audit_log(
            db=db,
            session=session,
            action="UPDATE",
            entity_type="EVENT_PHOTO",
            entity_id=photo.id,
            after_data={
                "caption": photo.caption,
                "sort_order": photo.sort_order,
            },
            details="Modification d'une photo du dossier événement.",
        )

        db.commit()
        db.refresh(photo)

        return photo

    except ValueError as exc:
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


# ============================================================
# SUPPRESSION
# ============================================================

@router.delete(
    "/{event_id}/photos/{photo_id}",
)
def remove_event_photo(
    event_id: int,
    photo_id: int,
    session=Depends(require_write_session),
):
    db = SessionLocal()

    try:
        photo = delete_event_photo(
            db=db,
            event_id=event_id,
            photo_id=photo_id,
        )

        write_audit_log(
            db=db,
            session=session,
            action="DELETE",
            entity_type="EVENT_PHOTO",
            entity_id=photo.id,
            before_data={
                "event_id": photo.event_id,
                "original_filename": photo.original_filename,
                "caption": photo.caption,
                "sort_order": photo.sort_order,
            },
            details="Suppression d'une photo du dossier événement.",
        )

                # Conserver le chemin avant de valider la suppression DB.
        storage_root = STORAGE_ROOT.parent.parent
        file_path = storage_root / photo.storage_path
        deleted_photo_id = photo.id

        # La base est validée en premier.
        db.commit()

        # Le fichier physique n'est supprimé qu'après succès du commit.
        if file_path.exists():
            file_path.unlink()

        return {
            "success": True,
            "deleted_photo_id": deleted_photo_id,
        }

    except ValueError as exc:
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()