import traceback

from .constants import LEVEL_DEBUG, LEVEL_INFO, LEVEL_WARNING, LEVEL_FATAL, LEVEL_ERROR, LEVEL_SUCCESS
import sys

class adislog_methods:
    def debug(self, *args, **kwargs):
        self._message(LEVEL_DEBUG,*args, **kwargs)
    
    def info(self, *args, **kwargs):
        self._message(LEVEL_INFO, *args, **kwargs)
        
    def warning(self, *args, **kwargs):
        self._message(LEVEL_WARNING, *args, **kwargs)
    
    def error(self, *args, **kwargs):
        self._message(LEVEL_ERROR, *args, **kwargs)
    
    def fatal(self,*args, **kwargs):
        self._message(LEVEL_FATAL, *args, **kwargs)
    
    def success(self, *args, **kwargs):
        self._message(LEVEL_SUCCESS, *args, **kwargs)
         
    def exception(self, message, as_fatal=True):
        excpt=self._probes.exception()
        self._message(
            log_level=4 if as_fatal else 3,
            log_item=message,
            exception_data=excpt
            )

    def exception_hook(self, ex_type, ex_value, ex_traceback):
        excpt=self._probes.exception(
            ex_type=ex_type, ex_value=ex_value, ex_traceback=ex_traceback)

        self._message(
            log_level=4,
            log_item='Uncaught exception',
            exception_data=excpt,
            depth=2
            )

        traceback.print_exception(ex_type, ex_value, ex_traceback)


        
