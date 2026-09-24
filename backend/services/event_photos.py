# ============================================================
# RISKY — SERVICE PHOTOS ÉVÉNEMENT
# ============================================================

from io import BytesIO
from pathlib import Path
from uuid import uuid4

from PIL import Image, ImageOps, UnidentifiedImageError
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend import models
from backend.domain_models.accident.event_photo import EventPhoto


# ============================================================
# CONFIGURATION
# ============================================================

MAX_PHOTOS_PER_EVENT = 4

MAX_UPLOAD_SIZE = 15 * 1024 * 1024  # 15 Mo

MAX_IMAGE_DIMENSION = 2000

JPEG_QUALITY = 85

ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
}

STORAGE_ROOT = (
    Path(__file__).resolve().parents[2]
    / "storage"
    / "event_photos"
)


# ============================================================
# OUTILS
# ============================================================

def _check_event_exists(
    db: Session,
    event_id: int,
) -> None:
    event = db.get(
        models.Event,
        event_id,
    )

    if event is None:
        raise ValueError("Événement introuvable.")


def _check_photo_limit(
    db: Session,
    event_id: int,
) -> None:
    count = db.scalar(
        select(func.count(EventPhoto.id))
        .where(
            EventPhoto.event_id == event_id,
        )
    )

    if (count or 0) >= MAX_PHOTOS_PER_EVENT:
        raise ValueError(
            "Le nombre maximum de 4 photos est atteint."
        )


def _event_storage_directory(
    event_id: int,
) -> Path:
    directory = STORAGE_ROOT / str(event_id)

    directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    return directory


# ============================================================
# VALIDATION ET OPTIMISATION
# ============================================================

def prepare_photo(
    content: bytes,
    content_type: str,
) -> tuple[bytes, str, str]:
    """
    Valide et optimise une photo.

    Retour :
        contenu optimisé,
        type MIME final,
        extension finale.
    """

    

    if len(content) > MAX_UPLOAD_SIZE:
        raise ValueError(
            "La photo dépasse la taille maximale de 15 Mo."
        )

    if not content:
        raise ValueError(
            "Le fichier photo est vide."
        )

    try:
        image = Image.open(BytesIO(content))
        image.load()
        original_format = image.format

        # ----------------------------------------------------
        # ORIENTATION DES PHOTOS SMARTPHONE
        # ----------------------------------------------------
        image = ImageOps.exif_transpose(image)

    except (UnidentifiedImageError, OSError) as exc:
            
        raise ValueError(
                "Le fichier n'est pas une image valide."
        ) from exc

    # --------------------------------------------------------
    # Vérification réelle du format
    # --------------------------------------------------------

    if original_format not in {
        "JPEG",
        "PNG",
    }:
        raise ValueError(
            "Format non autorisé. "
            "Seuls les fichiers JPEG et PNG sont acceptés."
        )

    # --------------------------------------------------------
    # Redimensionnement
    # --------------------------------------------------------

    if max(image.size) > MAX_IMAGE_DIMENSION:
        image.thumbnail(
            (
                MAX_IMAGE_DIMENSION,
                MAX_IMAGE_DIMENSION,
            ),
            Image.Resampling.LANCZOS,
        )

    output = BytesIO()

    # --------------------------------------------------------
    # JPEG
    # --------------------------------------------------------

    if original_format == "JPEG":
        if image.mode not in {
            "RGB",
            "L",
        }:
            image = image.convert("RGB")

        image.save(
            output,
            format="JPEG",
            quality=JPEG_QUALITY,
            optimize=True,
        )

        return (
            output.getvalue(),
            "image/jpeg",
            ".jpg",
        )

    # --------------------------------------------------------
    # PNG
    # --------------------------------------------------------

    image.save(
        output,
        format="PNG",
        optimize=True,
    )

    return (
        output.getvalue(),
        "image/png",
        ".png",
    )


# ============================================================
# AJOUT D'UNE PHOTO
# ============================================================

def create_event_photo(
    db: Session,
    event_id: int,
    original_filename: str,
    content_type: str,
    content: bytes,
    uploaded_by_person_id: int | None,
) -> EventPhoto:

    _check_event_exists(
        db=db,
        event_id=event_id,
    )

    _check_photo_limit(
        db=db,
        event_id=event_id,
    )

    (
        optimized_content,
        final_content_type,
        extension,
    ) = prepare_photo(
        content=content,
        content_type=content_type,
    )

    directory = _event_storage_directory(
        event_id,
    )

    stored_filename = (
        f"{uuid4().hex}{extension}"
    )

    file_path = (
        directory
        / stored_filename
    )

    file_path.write_bytes(
        optimized_content,
    )

    # --------------------------------------------------------
    # Ordre automatique
    # --------------------------------------------------------

    current_max_order = db.scalar(
        select(
            func.max(
                EventPhoto.sort_order,
            )
        )
        .where(
            EventPhoto.event_id == event_id,
        )
    )

    sort_order = (
        (current_max_order or 0)
        + 1
    )

    photo = EventPhoto(
        event_id=event_id,
        filename=stored_filename,
        original_filename=original_filename,
        content_type=final_content_type,
        file_size=len(optimized_content),
        storage_path=str(
            file_path.relative_to(
                STORAGE_ROOT.parent.parent,
            )
        ),
        sort_order=sort_order,
        uploaded_by_person_id=uploaded_by_person_id,
    )

    db.add(photo)
    db.flush()

    return photo


# ============================================================
# LECTURE
# ============================================================

def get_event_photos(
    db: Session,
    event_id: int,
) -> list[EventPhoto]:

    _check_event_exists(
        db=db,
        event_id=event_id,
    )

    return list(
        db.scalars(
            select(EventPhoto)
            .where(
                EventPhoto.event_id == event_id,
            )
            .order_by(
                EventPhoto.sort_order,
                EventPhoto.id,
            )
        ).all()
    )


# ============================================================
# MODIFICATION
# ============================================================

def update_event_photo(
    db: Session,
    event_id: int,
    photo_id: int,
    caption: str | None = None,
    sort_order: int | None = None,
) -> EventPhoto:

    photo = db.get(
        EventPhoto,
        photo_id,
    )

    if (
        photo is None
        or photo.event_id != event_id
    ):
        raise ValueError(
            "Photo introuvable."
        )

    if caption is not None:
        cleaned_caption = caption.strip()

        photo.caption = (
            cleaned_caption
            if cleaned_caption
            else None
        )

    if sort_order is not None:
        if sort_order < 1:
            raise ValueError(
                "L'ordre de la photo doit être supérieur à zéro."
            )

        photo.sort_order = sort_order

    db.flush()

    return photo

# ============================================================
# SUPPRESSION
# ============================================================

def delete_event_photo(
    db: Session,
    event_id: int,
    photo_id: int,
) -> EventPhoto:
    photo = db.get(EventPhoto, photo_id)

    if photo is None or photo.event_id != event_id:
        raise ValueError("Photo introuvable.")

    db.delete(photo)
    db.flush()

    return photo
