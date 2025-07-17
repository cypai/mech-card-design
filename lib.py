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
