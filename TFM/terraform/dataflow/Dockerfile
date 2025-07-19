FROM gcr.io/dataflow-templates-base/python3-template-launcher-base:latest

ENV FLEX_TEMPLATE_PYTHON_PY_FILE=/template/main.py
ENV FLEX_TEMPLATE_PYTHON_REQUIREMENTS_FILE=/template/requirements.txt

# Copy your pipeline code and requirements
COPY main.py /template/
COPY requirements.txt /template/

# Install dependencies and validate
RUN apt-get update && \
    apt-get install -y libffi-dev git && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir -U -r /template/requirements.txt && \
    (pip check || (e=$?; echo "Building a container with incompatible dependencies is prevented by default. If you are sure you want to proceed, you need to create your own container image. See: https://cloud.google.com/dataflow/docs/guides/templates/configuring-flex-templates"; exit $e))