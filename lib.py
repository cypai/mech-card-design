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
NUMBER_TAG_REGEX = re.compile(r"(\d|AP|\]) <:")
HEAT_COST_REGEX = re.compile(r"<:heat:> Cost")
TAG_NUMBER_REGEX = re.compile(r":> (\d)")
PERIOD_ENDS_REGEX = re.compile(r"!\)?\.$")


def wrap_text_tagged(text: str, width: int) -> str:
    preprocessed_text = re.sub(NUMBER_TAG_REGEX, r"\1<:", text)
    preprocessed_text = re.sub(TAG_NUMBER_REGEX, r":>\1", preprocessed_text)
    preprocessed_text = re.sub(HEAT_COST_REGEX, "<:heat:>Cost", preprocessed_text)
    untagged_text = re.sub(EMOJI_REGEX, "!", preprocessed_text)
    tags = EMOJI_REGEX.findall(text)

    paragraphs = untagged_text.splitlines()
    wrapped_paras = []

    wrapper = textwrap.TextWrapper(width=width)
    for para in paragraphs:
        if para.strip():
            wrapped_paras.extend(wrapper.wrap(para))
        else:
            wrapped_paras.append("\n")

    actual_paras = []
    for para in wrapped_paras:
        actual_para = para
        merge_with_prev_para = PERIOD_ENDS_REGEX.match(actual_para)
        while "!" in actual_para:
            actual_para = actual_para.replace("!", tags.pop(0), 1)
        if merge_with_prev_para is None:
            actual_paras.append(actual_para)
        else:
            actual_paras[-1] += actual_para

    return "\n".join(actual_paras)
