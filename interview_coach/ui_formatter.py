from state import usage, MODELS
from myagents.evaluator_agent import EvaluationResult


def format_usage(key='coach'):
    def get(field):
        return usage[f"{key}_{field}"]

    return (
        f"input {get('input'):,} | "
        f"output {get('output'):,} | "
        f"total {get('total'):,}"
    )


def format_usage_with_tokens(tokens, model, prefix='coach'):
    def get(field):
        return usage[f"{prefix}_{field}"]

    calculate_sum(model, prefix)

    usage_text = (f"inputs + {tokens['input_tokens']}: {get('input'):,} | "
                  f"output + {tokens['output_tokens']}: {get('output'):,} | "
                  f"total + {tokens['total_tokens']}: {get('total'):,} | "
                  f"${get('$'):.4f}")

    return usage_text


def calculate_sum(model, prefix):
    def get(field):
        return usage[f"{prefix}_{field}"]
    def set_money(value):
        usage[f"{prefix}_$"] = value

    prices = MODELS[model]
    money = get('input') * float(prices[1]) + get('output') * float(prices[2])
    money /= 1_000_000
    set_money(money)


def format_evaluation(message: str, history: str, evaluation_result: EvaluationResult):
    new_block = []

    new_block.append(message.strip())
    new_block.append("\n")
    new_block.append('**' + evaluation_result.corrected_phrase.strip() + '**')
    new_block.append("\n")

    if evaluation_result.notes:
        for note in evaluation_result.notes:
            new_block.append(f"- {note}")

    new_section = "\n".join(new_block).strip()

    if history and history.strip():
        return new_section + "\n\n---\n\n" + history.strip()

    return new_section
