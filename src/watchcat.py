import os
import threading
import time


class Watchcat(object):
    """Our main class which watch all changes on files."""

    def __init__(self, *files):
        self.files = []
        self.mod_times = {}
        self.num_changes = 0
        self._watching_thread = None
        self._watching_work = False

        if files:
            self.add_files(*files)

    def run_watching(self):
        """Watching on files, until get Ctrl+C."""
        self._watching_work = True
        self._watching_thread = threading.Thread(target=self._watch_till_stop)
        self._watching_thread.daemon = True
        self._watching_thread.start()

    def _watch_till_stop(self):
        """Work while _watching_work is True and main thread is alive."""
        while self._watching_work:
            if threading.main_thread().is_alive():
                self.watch_changes()
                time.sleep(1)
            else:
                self.stop_watching()

    def stop_watching(self):
        """Stop thread if conditions."""
        if self._watching_thread and self._watching_thread.isAlive():
            self._watching_work = False
            self._watching_thread.join()

    def watch_changes(self):
        """Memorize date of last changes and watching on them."""
        for file in self.files:
            try:
                last_mod_time = os.stat(file).st_mtime
            except OSError:
                time.sleep(1)
                last_mod_time = os.stat(file).st_mtime

            if file not in self.mod_times.keys():
                self.mod_times[file] = last_mod_time
                continue

            if last_mod_time > self.mod_times[file]:
                print("File changed: {}".format(os.path.realpath(file)))
                self.mod_times[file] = last_mod_time
                self.num_changes += 1

    def add_files(self, *files):
        """Func for adding files to self.files."""
        dirs = [os.path.realpath(x) for x in files if os.path.isdir(x)]
        files = [os.path.realpath(x) for x in files if os.path.isfile(x)]
        for i in dirs:
            files += self.get_files_in_dir(i)
        self.files = files
        self.watch_changes()

    def get_files_in_dir(self, dirname):
        """Recursive func for walking in dirs and finding files."""
        z = os.listdir(dirname)
        files = [dirname + '/' + x for x in z if os.path.isfile(dirname + '/' + x)]
        dirs = [dirname + '/' + x for x in z if os.path.isdir(dirname + '/' + x)]
        for i in dirs:
            files += self.get_files_in_dir(i)
        return files
