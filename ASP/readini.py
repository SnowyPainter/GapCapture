import configparser

def read(fname):
    config = configparser.ConfigParser()
    config.read(fname, encoding='utf-8')
    return {
        "AFFECTIVE" : config["AFFECTIVE"]["CODE"],
        "AF_BUY_THRESHOLD" : config["AFFECTIVE"].getfloat("BT"),
        "AF_SELL_THRESHOLD" : config["AFFECTIVE"].getfloat("ST"),
        "MODEL" : config["MODEL"]["PATH"],
        "TAG1" : config['SETTINGS']['SYMBOL1_TAG'],
        "TAG2" : config['SETTINGS']['SYMBOL2_TAG'],
        "SELL_AMOUNT" : config['SETTINGS'].getint('SELL_AMOUNT'),
        "BUY_AMOUNT" : config['SETTINGS'].getint('BUY_AMOUNT'),
        "CODE1" : config['SETTINGS']['SYMBOL1'],
        "CODE2" : config['SETTINGS']['SYMBOL2'],
        "NAME1" : config['SETTINGS']['SYMBOL1_NAME'],
        "NAME2" : config['SETTINGS']['SYMBOL2_NAME'],
        "FEE" : config['SETTINGS'].getfloat('FEE'),
        "TAKE_PROFIT" : config['SETTINGS'].getfloat('TAKE_PROFIT'),
        "STOP_LOSS" : config['SETTINGS'].getfloat('STOP_LOSS'),
    }