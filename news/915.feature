Added IBlockConverter concept, use named adapters to convert deserialized value
of blocks, this enables an extensible mechanism to transform block values on
add/edit content operations.

Added an html block converter, it will clean the
content of the "html" block according to portal_transform x-html-safe settings.

Move the resolveuid code from the dexterity field deserializer to a dedicated
block converter adapter, using the above mechanism.
[tiberiuichim]
