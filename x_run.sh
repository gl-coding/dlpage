function run_server() {
    nohup python3 manage.py runserver &
}

function download_videos() {
    python download_videos.py --json video_list_export.json
}

case $1 in
    "server")
        run_server
        ;;
    "download")
        download_videos
        ;;
    *)
        echo "Usage: $0 {server|download}"
        ;;
esac