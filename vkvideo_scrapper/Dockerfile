FROM continuumio/miniconda3:latest

WORKDIR /app

COPY environment.yml .

RUN conda env create -f environment.yml && conda clean -afy

COPY . .

EXPOSE 8501

ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "vkvideos", "streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
