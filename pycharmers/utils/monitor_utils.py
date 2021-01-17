# coding: utf-8
import os
import sys
import time

from ._colorings import toACCENT, toBLUE
from .generic_utils import readable_bytes
from .print_utils import visible_width

def progress_reporthook_create(filename="", bar_width=20, verbose=True):
    """Create Progress reporthook for ``urllib.request.urlretrieve``

    Returns:
        The ``reporthook`` which is a callable that accepts a ``block number``, a ``read size``, and the ``total file size`` of the URL target.

    Args:
        filename (str)  : Downloading filename.
        bar_width (int) : The width of progress bar.

    Examples:
        >>> import urllib
        >>> from pycharmers.utils import progress_reporthook_create
        >>> urllib.request.urlretrieve(url="hoge.zip", filename="hoge.zip", reporthook=progress_reporthook_create(filename="hoge.zip"))
        hoge.zip	1.5%[--------------------] 21.5[s] 8.0[GB/s]	eta 1415.1[s]
    """
    def progress_reporthook_verbose(block_count, block_size, total_size):
        global _reporthook_start_time
        if block_count == 0:
            _reporthook_start_time = time.time()
            return
        progress_size = block_count*block_size
        percentage = min(1.0, progress_size/total_size)
        progress_bar = ("#" * int(percentage * bar_width)).ljust(bar_width, "-")
        
        duration = time.time() - _reporthook_start_time
        speed = progress_size / duration
        eta = (total_size-progress_size)/speed

        speed, speed_unit = readable_bytes(speed)
        
        sys.stdout.write(f"\r{filename}\t{percentage:.1%}[{progress_bar}] {duration:.1f}[s] {speed:.1f}[{speed_unit}/s]\teta {eta:.1f}[s]")
        if progress_size >= total_size: print()
    def progress_reporthook_non_verbose(block_count, block_size, total_size):
        pass
    return progress_reporthook_verbose if verbose else progress_reporthook_non_verbose

class ProgressMonitor():
    """Monitor the loop progress.

    Examples:
        >>> from pycharmers.utils import ProgressMonitor
        >>> max_iter = 100
        >>> monitor = ProgressMonitor(max_iter=max_iter, verbose=1, barname="NAME")
        >>> for it in range(max_iter):
        >>>     monitor.report(it, loop=it+1)
        >>> monitor.remove()
        NAME 100/100[####################]100.00% - 0.010[s]  loop: 100
    """
    def __init__(self, max_iter, verbose=1, barname="", **kwargs):
        """
        Args:
            max_iter (int) : Maximum number of iterations.
            verbose (int)  : 0, 1, 2
                                * 0 : silent
                                * 1 : progress bar and metrics
                                * 2 : only progress bar
            barname (str)  : barname
        """
        self._init()
        self.max_iter = max_iter
        self.digit = len(str(max_iter))
        self.verbose = verbose
        self.barname = barname + " " if len(barname)>0 else ""
        self.report = {
            0 : self._report_silent,
            1 : self._report_progress_bar_and_metrics,
            2 : self._report_only_prograss_bar 
        }.get(verbose, self._report_progress_bar_and_metrics)
        self.report(it=-1)

    def _init(self):
        """Initialize the monitor."""
        self.histories = {}
        self.iter = 0
        self.prev_nrows = -1
        self.start_time = time.time()

    def write(self, string):
        """Use ASCI to output progress beautifully.

        * ``\\033[0J`` : Delete all strings after the cursor (including the following lines).
        * ``\\033[nF`` : Moves the cursor up ``n`` lines and then moves to the beginning of that line.

        Args:
            string : String to output.
        
        TODO:
            Determine ``nrows`` according to the previous output result.
        """
        if self.prev_nrows==-1:
            sys.stdout.write(string)
        elif self.prev_nrows==0:
            sys.stdout.write(f"\r{string}")
        else:
            sys.stdout.write(f"\033[{self.prev_nrows}F\033[0J{string}")
        sys.stdout.flush()
        self.prev_nrows = (visible_width(string)-1)//os.get_terminal_size().columns

    def progress(self, it):
        """Create a progress.
        
        Args:
            it (int) : Thr current iteration number.

        Returns:
            str : Thr current progress.        
        """
        it += 1
        return f"{self.barname}{it:>0{self.digit}}/{self.max_iter} [{('#' * int((it/self.max_iter)/0.05)).ljust(20, '-')}]{it/self.max_iter:>7.2%} - {time.time()-self.start_time:.3f}[s]"

    def _report_silent(self, it, **metrics):
        pass

    def _report_only_prograss_bar(self, it, **metrics):
        self.write(self.progress(it))

    def _report_progress_bar_and_metrics(self, it, **metrics):
        self.write(self.progress(it) + f"  {', '.join([f'{toACCENT(k)}: {toBLUE(v)}' for  k,v in metrics.items()])}")

    def remove(self):
        """Do the necessary processing at the end."""
        def _pass(*args, **kwargs):
            pass
        {
             0: _pass,
             1: sys.stdout.write,
             2: sys.stdout.write,
        }.get(self.verbose, sys.stdout.write)("\n")
