from state import usage
from evaluator_agent import EvaluationResult


def format_usage(key='coach'):
    def get(field):
        return usage[f"{key}_{field}"]

    return (
        f"input {get('input'):,} | "
        f"output {get('output'):,} | "
        f"total {get('total'):,}"
    )


def format_usage_with_tokens(tokens):
    usage_text = (f"inputs + {tokens['input_tokens']}: {usage['ev_input']:,} | "
                  f"output + {tokens['output_tokens']}: {usage['ev_output']:,} | "
                  f"total + {tokens['total_tokens']}: {usage['ev_total']:,}")
    return usage_text


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
