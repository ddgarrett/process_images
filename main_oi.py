'''
    Main program for Image Processing System - Organize Images Function

    Allow user to organize pictures into daily folders (YYYY-MM-DD)

    1. Set config function to be Organize Images
    2. call main.main

'''

import pi_config as c

if __name__ == '__main__':
    c.app_function = c.APP_ORG_IMG # running organize images
    import main
    main.main()
