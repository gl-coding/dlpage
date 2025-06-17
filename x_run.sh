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
    *)
        echo "Usage: $0 {server|download}"
        ;;
esac
