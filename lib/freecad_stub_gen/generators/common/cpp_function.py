from collections import deque
from collections.abc import Iterable, Iterator
from itertools import islice


def _skipAdditionalDirectiveBlocks(it: Iterator[tuple[int, str]]):
    directiveStack = [True]
    buffer: deque[str] = deque(maxlen=8)

    for index, char in it:
        buffer.append(char)
        if char in ' \n\t' and '#' in buffer:
            text = ''.join(buffer)[:-1]
            if text.endswith('#endif'):
                if len(directiveStack) > 1:
                    # there must exist at least one value,
                    # maybe we started in the middle of directive
                    directiveStack.pop()
                buffer.clear()
            elif text.endswith(('#elif', '#else')):
                directiveStack[-1] = False
                buffer.clear()
            elif text.endswith(('#if', '#ifdef', '#ifndef')):
                directiveStack.append(True)
                buffer.clear()

        if directiveStack[-1]:
            yield index, char


def findFunctionCall(
    text: str, bodyStart: int | None = None, bracketL='{', bracketR='}'
):
    if bodyStart is None:
        bodyStart = text.find('(')
    bracketDeep = 0

    sliceIt: Iterable[str] = islice(text, bodyStart, len(text))
    it = enumerate(sliceIt, bodyStart)
    if '#if' in text:
        it = _skipAdditionalDirectiveBlocks(it)

    bodyEnd = 0
    for i, char in it:
        bodyEnd = i
        if char == bracketL:
            bracketDeep += 1
        elif char == bracketR:
            bracketDeep -= 1
            if not bracketDeep:
                break

    return text[bodyStart : bodyEnd + 1]


def generateExpressionUntilChar(
    text: str, expStart: int = 0, splitChar: str = ',', bracketL='(', bracketR=')'
):
    if splitChar in f'\\"{bracketL}{bracketR}':
        msg = f"Cannot use {splitChar=} when generating expression"
        raise ValueError(msg)

    bracketDeep = 0
    expEnd = 0
    ignore = False
    escaped = False

    sliceIt = islice(text, expStart, len(text) + 1)
    for expEnd, char in enumerate(sliceIt, expStart):
        if escaped:
            escaped = False
        elif char == '\\':
            escaped = True
        elif char == '"':
            ignore = not ignore
        elif ignore:
            pass
        elif char in bracketL:
            bracketDeep += 1
        elif char in bracketR:
            bracketDeep -= 1
            if bracketDeep < 0:
                yield text[expStart:expEnd]
                return
        elif char == splitChar and bracketDeep == 0:
            yield text[expStart:expEnd]
            expStart = expEnd + 1

    yield text[expStart : expEnd + 1]


def genFuncArgs(text: str, textStart: int | None = None) -> Iterable[str]:
    funcCall = findFunctionCall(text, textStart, bracketL='(', bracketR=')')
    content = funcCall[funcCall.find('(') + 1 : funcCall.rfind(')')]
    for exp in generateExpressionUntilChar(content, splitChar=','):
        if e := exp.strip():
            yield e
