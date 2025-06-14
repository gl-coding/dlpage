function run_server() {
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
    *)
        echo "Usage: $0 {server|download}"
        ;;
esac