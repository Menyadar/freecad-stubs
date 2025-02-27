import re

from freecad_stub_gen.cpp_code.converters import removeQuote
from freecad_stub_gen.file_functions import genCppFiles, readContent
from freecad_stub_gen.generators.common.cpp_function import generateExpressionUntilChar
from freecad_stub_gen.generators.common.names import (
    getClassName,
    getModuleName,
    getNamespaceWithClass,
)
from freecad_stub_gen.module_namespace import moduleNamespace
from freecad_stub_gen.ordered_set import OrderedStrSet
from freecad_stub_gen.python_code import indent


class ExceptionData:
    def __init__(self, exceptionName: str, newExceptionArgs: list[str]):
        excModuleWithClass = removeQuote(newExceptionArgs[0])
        self.pyModuleRaw = getModuleName(excModuleWithClass, required=True)
        self.pyModule = moduleNamespace.convertNamespaceToModule(self.pyModuleRaw)
        self.pyClass = getClassName(excModuleWithClass)

        baseNamespace, self.baseCppClass = getNamespaceWithClass(newExceptionArgs[1])
        if baseNamespace is None:
            if self.baseCppClass.startswith('PyExc'):
                baseNamespace = '__python__'
            else:
                # no namespace means it is exception from current namespace
                baseNamespace = self.pyModuleRaw
        self.baseCppNamespace = baseNamespace

        self.cppNamespace, self.cppClass = getNamespaceWithClass(exceptionName)
        if self.cppClass == 'OCCError':  # there is additional assignment
            self.cppClass = 'PartExceptionOCCError'
        if self.cppNamespace is None:
            # no namespace means it is exception from current namespace
            self.cppNamespace = self.pyModuleRaw

        self.requiredImports = OrderedStrSet()

    def __str__(self):
        if self.baseCppNamespace == '__python__':
            baseClass = self.baseCppClass.removeprefix('PyExc_')
        else:
            ed = exceptionContainer.getExceptionData(
                self.baseCppClass, self.baseCppNamespace
            )
            self.requiredImports.add(ed.pyModule)
            baseClass = f'{ed.pyModule}.{ed.pyClass}'

        return f'class {self.pyClass}({baseClass}):\n{indent("pass")}\n'

    def __repr__(self):
        return (
            f'{self.pyModuleRaw}.{self.pyClass} [{self.cppNamespace}.{self.cppClass}]'
        )


class ExceptionContainer:
    REG_NEW_EXCEPTION = re.compile(
        r"""
    (?P<name>
        (\w+)                   # variable name
        (\s*::\s*\w+)?          # may be with namespace
    )
    \s*=\s*
    PyErr_NewException\(
    (?P<funArg>[^)]*)       # function arguments
    \);
    """,
        re.VERBOSE,
    )

    def __init__(self):
        self.exceptions = list(self._genExceptions())

    def checkAllExceptionsCorrect(self):
        for e in self.exceptions:
            repr(e)

    def _genExceptions(self):
        for file in genCppFiles():
            content = readContent(file)
            yield from self.findExceptions(content)

    @classmethod
    def findExceptions(cls, content):
        seen = set()  # there are two exception for OCCError
        for match in cls.REG_NEW_EXCEPTION.finditer(content):
            name = match.group('name')
            if name in seen:
                continue
            seen.add(name)

            fc = match.group('funArg')
            funArgs = [
                e.strip()
                for e in generateExpressionUntilChar(
                    fc, 0, ',', bracketL='(', bracketR=')'
                )
            ]

            ed = ExceptionData(name, funArgs)
            yield ed

    def getExceptionData(self, cppClass: str, cppNamespace: str):
        for e in self.exceptions:
            if e.cppClass == cppClass and e.cppNamespace == cppNamespace:
                return e

        msg = f'Cannot find exception: {cppClass=} {cppNamespace=}'
        raise ValueError(msg)

    def getExceptionText(self, cTypeExceptionText: str) -> str:
        _cppNamespace, cppClass = getNamespaceWithClass(cTypeExceptionText)
        for e in self.exceptions:
            if e.cppClass == cppClass:
                pyModule = e.pyModuleRaw if e.pyModuleRaw != 'Base' else 'FreeCAD.Base'
                return f'{pyModule}.{e.pyClass}'

        if cTypeExceptionText.startswith('PyExc_'):
            return cTypeExceptionText.removeprefix('PyExc_')

        if 'getPyExceptionType()' in cTypeExceptionText:
            # The return type of this c++ function is PyObject.
            # An implementation return in this function various FreeCAD exceptions,
            # but we are unable to determine which one is used.
            return 'Exception'

        msg = f'Unknown exception {cTypeExceptionText=}'
        raise ValueError(msg)


exceptionContainer = ExceptionContainer()
exceptionContainer.checkAllExceptionsCorrect()
