# 判断如果是linux系统，则指定python3路径
if [ "$(uname)" == "Linux" ]; then
    PYTHON_PATH="/root/miniconda3/envs/py310/bin/python"
else
    PYTHON_PATH="python"
fi

function run_server() {
    ps -ef | grep python | grep runserver | awk '{print $2}' | xargs kill -9
    nohup $PYTHON_PATH  manage.py runserver &
}

function download_videos() {
    $PYTHON_PATH download_videos.py --json video_list_export.json
}

function export_links() {
    $PYTHON_PATH download_videos.py --export-links
}

function download_from_links() {
    $PYTHON_PATH download_videos.py --download
}

function download_from_api() {
    $PYTHON_PATH download_videos.py --api --mapping download_mapping.txt
}

function upload_video_text() {
    $PYTHON_PATH upload_video_text.py --dir video_audio/transcriptions
}

function server_all() {
    # 如果timestamp.txt存在，则下载
    if [ -f timestamp.txt ]; then
        echo "timestamp.txt exists, running, date: `date`" >> log.run
        if [ -f x_status ]; then
            echo "x_status exists, date: `date`" >> log.run
            exit 0
        fi
        echo "running" > x_status
        echo "task begin, date: `date`" >> log.run
        rm -rf downloaded_videos/
        rm -f download_mapping.txt
        download_from_api >> log.run 2>&1
        cd video_audio2txt
        sh x_run_all.sh >> log.run 2>&1
        cd ..
        mv x_status x_status.old
        rm -f timestamp.txt 
    else
        echo "timestamp.txt not found, skipping download, date: `date`" > log.run
    fi
}

function local_all() {
    rm -rf downloaded_videos/
    rm -f download_mapping.txt
    download_from_api
    cd video_audio2txt
    sh x_run_all.sh
    cd ..
}

function clean() {
    rm -rf downloaded_videos/
    rm -f download_mapping.txt
    rm -f timestamp.txt
    rm -f x_status*
    rm -rf video_audio/
}

case $1 in
    "server")
        run_server
        ;;
    "download")
        download_videos
        ;;
    "export")
        export_links
        ;;
    "dlurl")
        download_from_links
        ;;
    "dlapi")
        download_from_api
        ;;
    "upload")
        upload_video_text
        ;;
    "server_all")
        server_all
        ;;
    "local_all")
        local_all
        ;;
    "clean")
        clean
        ;;
    *)
        echo "Usage: $0 {server|download|export|dlurl|dlapi|upload|all}"
        ;;
esac
