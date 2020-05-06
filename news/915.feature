Added IBlockDeserializer and its counterpart, IBlockSerializer concepts, use
subscribers to convert/adjust value of blocks on serialization/deserialization,
this enables an extensible mechanism to transform block values when saving content.

Added an html block deserializer, it will clean the
content of the "html" block according to portal_transform x-html-safe settings.

Added an image block deserializer, it will use resolveuid mechanism to
transform the url field to a UID of content.

Move the resolveuid code from the dexterity field deserializer to a dedicated
block converter adapter, using the above mechanism.
[tiberiuichim]
