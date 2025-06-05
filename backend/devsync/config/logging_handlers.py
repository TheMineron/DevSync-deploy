import glob
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime


class DailyRotatingFileHandler(RotatingFileHandler):
    def __init__(self, filename, maxBytes=10 * 1024 * 1024, backupCount=0,
                 encoding=None, delay=False, max_days = 7):
        self._date_folder = datetime.now().strftime("%Y-%m-%d")
        self._base_filename = filename
        self._ensure_date_folder_exists()
        self.max_days = max_days

        full_path = os.path.join(self._get_logs_folder(), filename)

        super().__init__(
            filename=full_path,
            maxBytes=maxBytes,
            backupCount=backupCount,
            encoding=encoding,
            delay=delay
        )
        self._clean_old_logs()

    def _clean_old_logs(self):
        now = datetime.now()
        log_folders = self._get_all_log_folders()

        for folder in log_folders:
            try:
                folder_date = os.path.basename(os.path.normpath(folder))
                folder_datetime = datetime.strptime(folder_date, "%Y-%m-%d")
                if (now - folder_datetime).days > self.max_days:
                    import shutil
                    shutil.rmtree(folder)
            except (ValueError, OSError):
                continue

    def _get_all_log_folders(self):
        log_dir = os.path.dirname(self._get_logs_folder())
        return glob.glob(os.path.join(log_dir, "*/"))

    def _get_logs_folder(self):
        return os.path.join("logs", self._date_folder)

    def _ensure_date_folder_exists(self):
        logs_folder = self._get_logs_folder()
        if not os.path.exists(logs_folder):
            os.makedirs(logs_folder)

    def shouldRollover(self, record):
        if self.stream is None:
            self.stream = self._open()

        if self.maxBytes > 0:
            msg = "%s\n" % self.format(record)
            self.stream.seek(0, 2)  # в конец файла
            if self.stream.tell() + len(msg) >= self.maxBytes:
                return 1
        current_date = datetime.now().strftime("%Y-%m-%d")
        if current_date != self._date_folder:
            return 2

        return 0

    def doRollover(self):
        if self.stream:
            self.stream.close()

        if self.backupCount > 0:
            for i in range(self.backupCount - 1, 0, -1):
                sfn = "%s.%d" % (self.baseFilename, i)
                dfn = "%s.%d" % (self.baseFilename, i + 1)
                if os.path.exists(sfn):
                    if os.path.exists(dfn):
                        os.remove(dfn)
                    os.rename(sfn, dfn)

            dfn = self.baseFilename + ".1"
            if os.path.exists(dfn):
                os.remove(dfn)
            os.rename(self.baseFilename, dfn)

        current_date = datetime.now().strftime("%Y-%m-%d")
        if current_date != self._date_folder:
            self._date_folder = current_date
            self._ensure_date_folder_exists()
            self.baseFilename = os.path.join(
                self._get_logs_folder(),
                self._base_filename
            )
            self._clean_old_logs()

        self.stream = self._open()
