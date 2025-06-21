function run_server() {
    ps -ef | grep python | grep runserver | awk '{print $2}' | xargs kill -9
    nohup python3 manage.py runserver &
}

function download_videos() {
    python download_videos.py --json video_list_export.json
}

function export_links() {
    python download_videos.py --export-links
}

function download_from_links() {
    python download_videos.py --download
}

function download_from_api() {
    python download_videos.py --api --mapping download_mapping.txt
}

function upload_video_text() {
    python upload_video_text.py --dir video_audio/transcriptions
}

function all() {
    # 如果timestamp.txt存在，则下载
    if [ -f timestamp.txt ]; then
        if [ -f x_status ]; then
            echo "x_status exists, skipping download"
            exit 0
        fi
        echo "running" > x_status
        download_from_api
        cd video_audio2txt
        sh x_run_all.sh
        cd ..
        #upload_video_text
        mv x_status x_status.old
    fi
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
    "all")
        all
        ;;
    *)
        echo "Usage: $0 {server|download|export|dlurl|dlapi|upload|all}"
        ;;
esac
