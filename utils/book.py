from utils.book_num import get_book_nums_main
from utils.book_author import get_author
from utils.book_chapter import get_chapter
from utils.book_detail import get_book_detail
import time


def book_main():
    start = time.time()
    print('-----------------book starting--------------------')

    print('-----------------get_book_nums_main() starting--------------------')
    get_book_nums_main()
    print('-----------------get_book_nums_main ended--------------------')

    print('-----------------get_book_detail(man) starting--------------------')
    get_book_detail(True)
    print('-----------------get_book_detail(man) ended--------------------')

    print('-----------------get_book_detail(mm) starting--------------------')
    get_book_detail(False)
    print('-----------------get_book_detail(mm) ended--------------------')

    print('-----------------get_author() starting--------------------')
    get_author()
    print('-----------------get_author() ended--------------------')

    print('-----------------get_chapter() starting--------------------')
    get_chapter()
    print('-----------------get_chapter() ended--------------------')

    print('-----------------book ended--------------------')
    end = time.time()
    period = end - start
    print('Total spent %d m %d s' % (int(period) / 60, int(period) % 60))

if __name__ == '__main__':
    book_main()

