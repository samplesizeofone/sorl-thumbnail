#coding=utf-8
from sorl.thumbnail.helpers import toint
from sorl.thumbnail.parsers import parse_crop, parse_trim


class EngineBase(object):
    """
    ABC for Thumbnail engines, methods are static
    """
    def create(self, image, geometry, options):
        """
        Processing conductor, returns the thumbnail as an image engine instance
        """
        image = self.colorspace(image, geometry, options)
        image = self.trim(image, geometry, options)
        image = self.scale(image, geometry, options)
        image = self.crop(image, geometry, options)
        return image

    def colorspace(self, image, geometry, options):
        """
        Wrapper for ``_colorspace``
        """
        colorspace = options['colorspace']
        return self._colorspace(image, colorspace)

    def scale(self, image, geometry, options):
        """
        Wrapper for ``_scale``
        """
        crop = options['crop']
        upscale = options['upscale']
        x_image, y_image = map(float, self.get_image_size(image))
        # calculate scaling factor
        factors = (geometry[0] / x_image, geometry[1] / y_image)
        factor = max(factors) if crop else min(factors)
        if factor < 1 or upscale:
            width = toint(x_image * factor)
            height = toint(y_image * factor)
            image = self._scale(image, width, height)
        return image

    def crop(self, image, geometry, options):
        """
        Wrapper for ``_crop``
        """
        crop = options['crop']
        if not crop or crop == 'noop':
            return image
        x_image, y_image = self.get_image_size(image)
        x_offset, y_offset = parse_crop(crop, (x_image, y_image), geometry)
        return self._crop(image, geometry[0], geometry[1], x_offset, y_offset)

    def trim(self, image, geometry, options):
        """
        Wrapper for ``_trim``
        """
        trim = options.get('trim', None)

        if not trim or trim == 'noop':
            return image
        
        x_image, y_image = self.get_image_size(image)

        x_offset, y_offset, width, height = parse_trim(trim, (x_image, y_image), geometry)

        return self._crop(image, width, height, x_offset, y_offset)

    def write(self, image, options, thumbnail):
        """
        Wrapper for ``_write``
        """
        format_ = options['format']
        quality = options['quality']
        raw_data = self._get_raw_data(image, format_, quality)
        thumbnail.write(raw_data)

    def get_image_ratio(self, image):
        """
        Calculates the image ratio
        """
        x, y = self.get_image_size(image)
        return float(x) / y

    #
    # Methods which engines need to implement
    # The ``image`` argument refers to a backend image object
    #
    def get_image(self, source):
        """
        Returns the backend image objects from a ImageFile instance
        """
        raise NotImplemented()

    def get_image_size(self, image):
        """
        Returns the image width and height as a tuple
        """
        raise NotImplemented()

    def is_valid_image(self, raw_data):
        """
        Checks if the supplied raw data is valid image data
        """
        raise NotImplemented()

    def _colorspace(self, image, colorspace):
        """
        `Valid colorspaces
        <http://www.graphicsmagick.org/GraphicsMagick.html#details-colorspace>`_.
        Backends need to implement the following::

            RGB, GRAY
        """
        raise NotImplemented()

    def _scale(self, image, width, height):
        """
        Does the resizing of the image
        """
        raise NotImplemented()

    def _crop(self, image, width, height, x_offset, y_offset):
        """
        Crops the image
        """
        raise NotImplemented()

    def _get_raw_data(self, image, format_, quality):
        """
        Gets raw data given the image, format and quality. This method is
        called from :meth:`write`
        """
        raise NotImplemented()

