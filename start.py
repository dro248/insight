from subprocess import Popen, run

if __name__ == '__main__':
    # Run Streamlit backend
    # streamlit run streamlit_backend.py
    # streamlit_proc = Popen('streamlit run streamlit_backend.py'.split())
    panel_proc = Popen('python -m panel serve graphs/graph_notebook.ipynb'.split())
    print(f"panel_proc.pid: {panel_proc.pid}")

    # Run Insight Engine
    # python -m engine.run_loop &
    insight_engine_proc = Popen('python -m engine.run_loop'.split())
    print(f"insight_engine_proc.pid: {insight_engine_proc.pid}")

    # Run Flask app (with socket.io)
    # python -m app.routes &
    flask_app_proc = run('python -m app.routes'.split())
    print(f"flask_app_proc.pid: {flask_app_proc.pid}")
