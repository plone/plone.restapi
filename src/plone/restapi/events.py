""" Custom events handlers
"""
from lxml import etree

NAMESPACE = '{http://namespaces.plone.org/supermodel/schema}'
AUTO_DISABLE_BEHAVIORS = ("volto.blocks", "plone.restapi.behaviors.IBlocks")
CUSTOM_BLOCKS_SCHEMA = """
<model xmlns="http://namespaces.plone.org/supermodel/schema">
  <schema>
    <fieldset name="layout" label="Layout">
      <field name="blocks" type="plone.schema.jsonfield.JSONField">
        <title>Blocks</title>
        <default>{}</default>
      </field>
      <field name="blocks_layout" type="plone.schema.jsonfield.JSONField">
        <title>Blocks Layout</title>
        <default>{"items": []}</default>
      </field>
    </fieldset>
  </schema>
</model>
"""


def handleCustomVoltoBlocks(object, event):
    fti = getattr(object, "fti", None)
    behaviors = getattr(fti, "behaviors", [])

    if "volto.blocks.custom" in behaviors:
        object.fti.behaviors = [b for b in behaviors if b not in AUTO_DISABLE_BEHAVIORS]

        model_source = getattr(fti, 'model_source', '').strip()

        # Custom Blocks Layout already within fti model
        if 'name="blocks_layout"' in model_source or 'name="blocks"' in model_source:
            return

        if not model_source:
            return fti.manage_changeProperties(model_source=CUSTOM_BLOCKS_SCHEMA)

        parser = etree.XMLParser(resolve_entities=False, remove_pis=True)
        root = etree.fromstring(model_source, parser=parser)
        schema = root.find(NAMESPACE + 'schema')
        if not schema:
            return fti.manage_changeProperties(model_source=CUSTOM_BLOCKS_SCHEMA)

        custom_model = etree.fromstring(CUSTOM_BLOCKS_SCHEMA, parser=parser)
        custom_schema = custom_model.find(NAMESPACE + 'schema')
        custom_fieldset = custom_schema.find(NAMESPACE + 'fieldset')

        schema.extend(custom_fieldset)
        custom_source = etree.tostring(
            root,
            pretty_print=True,
            xml_declaration=True,
            encoding='utf8'
        )

        return fti.manage_changeProperties(model_source=custom_source)
