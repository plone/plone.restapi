from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.globalrequest import getRequest


def get_scales(context, field, width, height):
    """Get a dictionary of available scales for a particular image field,
    with the actual dimensions (aspect ratio of the original image).
    """
    scales = {}
    request = getRequest()
    images_view = getMultiAdapter((context, request), name="images")

    for name, actual_width, actual_height in get_scale_infos():
        # Try first with scale name
        scale = images_view.scale(field.__name__, scale=name)
        if scale is None:
            # Sometimes it fails, but we can create it
            # using scale sizes
            scale = images_view.scale(
                field.__name__, width=actual_width, height=actual_height
            )

        if scale is None:
            # If we still can't get a scale, it's probably a corrupt image
            continue

        url = scale.url
        actual_width = scale.width
        actual_height = scale.height

        scales[name] = {
            "download": url,
            "width": actual_width,
            "height": actual_height,
        }

    return scales


def get_original_image_url(context, fieldname, width, height):
    request = getRequest()
    images_view = getMultiAdapter((context, request), name="images")
    scale = images_view.scale(
        fieldname, width=width, height=height, direction="thumbnail"
    )
    if scale:
        return scale.url
    # Corrupt images may not have a scale.


def get_actual_scale(dimensions, bbox):
    """Given dimensions of an original image, and a bounding box of a scale,
    calculates what actual dimensions that scaled image would have,
    maintaining aspect ratio.

    This is supposed to emulate / predict the behavior of Plone's
    ImageScaling implementations.
    """
    width, height = dimensions
    max_width, max_height = bbox
    resize_ratio = min(max_width / width, max_height / height)

    # Plone doesn't upscale images for the default named scales - limit
    # to actual image dimensions
    resize_ratio = min(resize_ratio, 1.0)

    scaled_dimensions = int(width * resize_ratio), int(height * resize_ratio)

    # Don't produce zero pixel lengths
    scaled_dimensions = tuple(max(1, dim) for dim in scaled_dimensions)
    return scaled_dimensions


def get_scale_infos():
    """Returns a list of (name, width, height) 3-tuples of the
    available image scales.
    """
    from plone.registry.interfaces import IRegistry

    registry = getUtility(IRegistry)
    from Products.CMFPlone.interfaces import IImagingSchema

    imaging_settings = registry.forInterface(IImagingSchema, prefix="plone")
    allowed_sizes = imaging_settings.allowed_sizes

    def split_scale_info(allowed_size):
        name, dims = allowed_size.split(" ")
        width, height = list(map(int, dims.split(":")))
        return name, width, height

    return [split_scale_info(size) for size in allowed_sizes]
