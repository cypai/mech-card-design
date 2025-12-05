import re
import textwrap
from wand.drawing import Drawing


def wrap_text(ctx: Drawing, text: str, roi_width: int):
    paragraphs = text.splitlines()
    wrapped_paras = []

    estimated_columns = int(roi_width / (ctx.font_size * 0.6))
    wrapper = textwrap.TextWrapper(width=estimated_columns, break_long_words=True)
    for para in paragraphs:
        if para.strip():
            wrapped_paras.extend(wrapper.wrap(para))
        else:
            wrapped_paras.append("\n")

    return "\n".join(wrapped_paras)


EMOJI_REGEX = re.compile("<:[a-zA-Z0-9_-]{1,32}:>")


def wrap_text_tagged(text: str, width: int) -> str:
    untagged_text = re.sub(EMOJI_REGEX, "!", text)
    tags = EMOJI_REGEX.findall(text)

    paragraphs = untagged_text.splitlines()
    wrapped_paras = []

    wrapper = textwrap.TextWrapper(width=width)
    for para in paragraphs:
        if para.strip():
            wrapped_paras.extend(wrapper.wrap(para))
        else:
            wrapped_paras.append("\n")

    for para in wrapped_paras:
        actual_para = para
        while "!" in actual_para:
            actual_para = actual_para.replace("!", tags.pop(0), 1)

    return "\n".join(wrapped_paras)
