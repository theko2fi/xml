#!/bin/ksh
# remove_kusers.ksh
# Simple, safe remover for "k+uid" users. Backs up /etc/passwd and /etc/shadow first.

pattern='^k[a-z][0-9]+$'
dry_run=0
force=0
logfile="./remove_kusers.log"
backup_root="/var/backups/remove_kusers"

usage() {
  echo "Usage: $0 [-n] [-f] [-p pattern] [-l logfile] [-b backup_dir]"
  echo "  -n           Dry-run (show what would be removed)"
  echo "  -f           Force remove without prompts"
  echo "  -p pattern   Regex pattern for usernames (default: ^k[a-z][0-9]+$)"
  echo "  -l logfile   Log file (default: ./remove_kusers.log)"
  echo "  -b backupdir Directory to store passwd/shadow backups (default: /var/backups/remove_kusers)"
  exit 1
}

while getopts ":nfp:l:b:h" opt; do
  case $opt in
    n) dry_run=1 ;;
    f) force=1 ;;
    p) pattern="$OPTARG" ;;
    l) logfile="$OPTARG" ;;
    b) backup_root="$OPTARG" ;;
    h) usage ;;
    *) usage ;;
  esac
done

if [ "$(id -u)" -ne 0 ]; then
  echo "This script must be run as root." >&2
  exit 2
fi

# Determine UID_MIN from /etc/login.defs (fallback 1000)
UID_MIN=1000
if [ -r /etc/login.defs ]; then
  v=$(awk '/^UID_MIN/ {print $2; exit}' /etc/login.defs 2>/dev/null)
  if [ -n "$v" ]; then
    UID_MIN=$v
  fi
fi

tmpfile=$(mktemp)
trap 'rm -f "$tmpfile"' EXIT
awk -F: -v min="$UID_MIN" -v pat="$pattern" '($3 >= min && $1 ~ pat){ print $1 ":" $3 ":" $6 }' /etc/passwd > "$tmpfile"

if [ ! -s "$tmpfile" ]; then
  echo "No matching users found for pattern: $pattern"
  exit 0
fi

count=$(wc -l < "$tmpfile" | tr -d ' ')
echo "Found $count candidate(s) matching pattern: $pattern"

timestamp() { date +"%Y-%m-%d %H:%M:%S"; }
log() { echo "$(timestamp) - $*" >> "$logfile"; }

# Backup passwd and shadow unless dry-run
if [ "$dry_run" -eq 0 ]; then
  ts=$(date +%Y%m%d%H%M%S)
  backup_dir="$backup_root/$ts"
  mkdir -p "$backup_dir" || { echo "Failed to create backup dir $backup_dir"; exit 3; }
  if cp -a /etc/passwd /etc/shadow "$backup_dir/" 2>/dev/null; then
    echo "Backed up /etc/passwd and /etc/shadow to $backup_dir"
    log "BACKUP saved to=$backup_dir"
  else
    echo "Failed to backup /etc/passwd or /etc/shadow. Aborting." >&2
    log "BACKUP_FAILED dir=$backup_dir"
    exit 4
  fi
else
  echo "Dry-run: skipping backup step"
fi

echo "--- Candidates ---"
awk -F: '{ printf("%s  UID=%s  HOME=%s\n", $1, $2, $3) }' "$tmpfile"

if [ "$dry_run" -eq 1 ]; then
  echo "Dry-run: no changes will be made. See log: $logfile"
  exit 0
fi

# Single confirmation for all candidates
if [ "$force" -ne 1 ]; then
  printf "Remove ALL %s users shown above? [y/N]: " "$count"
  read ans
  case "$ans" in
    y|Y) proceed_all=1 ;;
    *) echo "Aborted by user."; exit 0 ;;
  esac
else
  proceed_all=1
fi

while IFS=":" read user uid home; do
  if [ "$proceed_all" -eq 1 ]; then
    echo "Removing $user..."
    if /usr/sbin/deluser -r "$user" >/dev/null 2>&1; then
      echo "Removed $user"
      log "REMOVED user=$user uid=$uid home=$home"
    else
      echo "Failed to remove $user -- see $logfile"
      log "FAILED_REMOVE user=$user uid=$uid home=$home"
    fi
  fi
done < "$tmpfile"

echo "Completed. See log: $logfile"
exit 0
