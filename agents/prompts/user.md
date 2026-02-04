# EVALUATION TASK
Evaluate the quality of the generated summary provided below.

### DATA INPUTS
**Generated Summary:** {{ generated_summary }}

{% if source %}
**Source Text:** {{ source }}
{% endif %}

{% if reference_summary %}
**Reference Summary:** {{ reference_summary }}
{% endif %}

### INSTRUCTIONS
1. **Scenario Detection:** You have been provided with 
   {%- if source and reference_summary %} both the Source and a Reference summary.
   {%- elif source %} only the Source text.
   {%- elif reference_summary %} only a Reference summary.
   {%- else %} neither the Source nor a Reference.
   {%- endif %}
2. **Metric Selection:** Refer to your SYSTEM PROMPT decision guide and run the `recommend` tool for this specific scenario.
3. **Execution:** Call the appropriate metrics via `tool_logic.py`.
4. **Synthesis:** Provide a final quality assessment based on the results.