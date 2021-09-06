import inspect
import xml.etree.ElementTree as ET
from distutils.util import strtobool
from pathlib import Path
from typing import Optional

from freecad_stub_gen.config import SOURCE_DIR
from freecad_stub_gen.generators.method.method import MethodGenerator
from freecad_stub_gen.generators.names import getBaseClasses, getSimpleClassName, \
    getShortModuleFormat
from freecad_stub_gen.generators.property import PropertyGenerator
from freecad_stub_gen.stub_container import StubContainer


class FreecadStubGeneratorFromXML(PropertyGenerator, MethodGenerator):
    """Generate class defined in xml file.
    Argument types are extracted from code."""

    def __init__(self, filePath: Path, sourceDir: Path = SOURCE_DIR):
        super().__init__(filePath, sourceDir)
        self.currentNode = None

    def getStub(self) -> Optional[StubContainer]:
        header = f'# {self.baseGenFilePath.name}\n'
        content = '\n'.join(self._parseFile())
        return StubContainer(header + content, self.requiredImports)

    def _parseFile(self) -> str:
        tree = ET.parse(self.baseGenFilePath)
        root = tree.getroot()

        for child in root:
            if child.tag == 'PythonExport':
                self.currentNode = child
                yield self.genClass()

    def genClass(self):
        baseClasses = ', '.join(self.genBaseClasses())
        className = getSimpleClassName(self.currentNode)
        classStr = f"class {className}({baseClasses}):\n"
        if doc := self._genDocFromStr(self._getDocFromNode(self.currentNode)):
            classStr += self.indent(doc)
            classStr += '\n'
        classStr += self.indent(self.genInit())

        if specialCaseCode := self.getCodeForSpecialCase(className):
            classStr += self.indent(specialCaseCode)

        for attributeNode in sorted(self.currentNode.findall('Attribute'), key=self._nodeSort):
            classStr += self.indent(self.getAttributes(attributeNode))

        for methodNode in sorted(self.currentNode.findall('Methode'), key=self._nodeSort):
            classStr += self.indent(self.genMethod(methodNode))

        if strtobool(self.currentNode.attrib.get('RichCompare', 'False')):
            classStr += self.indent(self.genRichCompare())
        if strtobool(self.currentNode.attrib.get('NumberProtocol', 'False')):
            classStr += self.indent(self.genNumberProtocol(className))

        return classStr

    @staticmethod
    def _nodeSort(node: ET.Element):
        return node.attrib['Name']

    def genBaseClasses(self):
        for base in getBaseClasses(self.currentNode):
            # self.requiredImports.add(base[:base.rfind('.')])
            module, base = getShortModuleFormat(base)  # workaround
            self.requiredImports.add(module)
            yield base

    def getCodeForSpecialCase(self, className: str) -> str:
        ret = ''
        if className == 'DocumentObject':
            ret += self.getProperty('Label', 'str', readOnly=False)
            ret += self.getProperty('Proxy', 'FreeCADTemplates.ProxyPython', readOnly=False)
            self.requiredImports.add('FreeCADTemplates')

        elif className == 'ViewProviderDocumentObject':
            ret += self.getProperty(
                'DisplayMode', 'typing.Optional[int]', docs="Set the display mode", readOnly=False)
            ret += self.getProperty('Proxy', 'FreeCADTemplates.ViewProviderPython', readOnly=False)
            self.requiredImports.add('FreeCADTemplates')
            ret += self.getProperty(
                'OnTopWhenSelected',
                'typing.Union[int, typing.Literal["Disabled", "Enabled", "Object", "Element"]]',
                "Enabled: Display the object on top of any other object when selected\n"
                "Object: On top only if the whole object is selected\n"
                "Element: On top only if some sub-element of the object is selected",
                readOnly=False)
            ret += self.getProperty(
                'SelectionStyle', 'typing.Union[int, typing.Literal["Shape", "BoundBox"]]',
                docs="Set the object selection style", readOnly=False)
            ret += self.getProperty(
                'ShowInTree', 'bool', docs="Show the object in the tree view", readOnly=False)
            ret += self.getProperty(
                'Visibility', 'bool', docs="Show the object in the 3d view", readOnly=False)

        elif className == 'GroupExtension':
            ret += self.getProperty('Group', 'list[DocumentObject]', readOnly=False)

        elif className == 'Workbench':
            ret += workbenchBody + '\n\n'

        return ret


workbenchBody = inspect.cleandoc("""
    MenuText = ""
    ToolTip = ""
    
    def Initialize(self):
        raise NotImplementedError
    
    def ContextMenu(self, recipient): ...
    
    def appendToolbar(self, name, cmds): ...
    
    def removeToolbar(self, name): ...
    
    def appendCommandbar(self, name, cmds): ...
    
    def removeCommandbar(self, name): ...
    
    def appendMenu(self, name, cmds): ...
    
    def removeMenu(self, name): ...
    
    def appendContextMenu(self, name, cmds): ...
    
    def removeContextMenu(self, name): ...
    
    def GetClassName(self): ...
""")
