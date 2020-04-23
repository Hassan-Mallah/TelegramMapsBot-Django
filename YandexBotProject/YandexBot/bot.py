# comments on the code
# empty DB
# name of search areas in admin
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, ConversationHandler)
import requests
from .models import SearchResult, TelegramUser, SearchAreas


CHOOSING, SEARCH = range(2)

# Will give user 2 options
def start(update, context):
    reply_keyboard = [['Search', 'History']]
    update.message.reply_text('Please Choose:', reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return CHOOSING


def search(update, context):
    update.message.reply_text('What do you want to Search: \n or /cancel to stop!', reply_markup=ReplyKeyboardRemove())
    return SEARCH


def result(update, context):
    # Yandex API and key
    url = 'https://geocode-maps.yandex.ru/1.x/?apikey=fa55c0df-c4f5-4962-8cc8-921cc8f442b9&format=json&results=1&geocode='
    query = update.message.text
    user = update.message.from_user

    # request from API according to areas
    areas = SearchAreas.objects.all()
    t = 'not found'
    for i in areas:
        r = requests.get(url + i.area + ' ' + query).json()['response']['GeoObjectCollection']['featureMember']
        if r != []:
            t = r[0]['GeoObject']['metaDataProperty']['GeocoderMetaData']['Address']['formatted']
            break

    # save to DB
    searchresult = SearchResult()
    searchresult.result = t
    searchresult.query = query
    searchresult.save()

    telegramuser = TelegramUser()
    telegramuser.telegram_id = user.id
    telegramuser.result_id = searchresult
    telegramuser.save()

    # print result to user
    update.message.reply_text('Result ' + t)
    update.message.reply_text('/start again!')
    return ConversationHandler.END


def history(update, context):
    from .models import SearchResult, TelegramUser
    user = update.message.from_user
    id = user.id

    # sort and get the 5 latest records + count of records for this user
    records_count = TelegramUser.objects.filter(telegram_id=id).count()
    update.message.reply_text('Вы совершили ' + str(records_count) + ' поисковых запросов.',
                              reply_markup=ReplyKeyboardRemove())
    # if the user has has records
    if records_count > 0:
        queryset = TelegramUser.objects.filter(telegram_id=id).order_by('-result_id')[:5]

        string = ''
        for record in queryset:
            string += record.result_id.query + ' -> ' + str(record.result_id.result) + ' ( ' + str(
                record.result_id.query_date.date()) + ' )\n '
        update.message.reply_text(string)

    update.message.reply_text('/start again!')

    return ConversationHandler.END


def cancel(update, context):
    update.message.reply_text('Bye! I hope we can talk again some day.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def main():
    # Token and VPN/SOCKS
    TOKEN = '1136453226:AAHbKj56CeWiynkg3jShCE7rdvDm_oUwgII'
    REQUEST_KWARGS = {
        'proxy_url': 'socks5://localhost:9150',
    }
    updater = Updater(TOKEN, request_kwargs=REQUEST_KWARGS, use_context=True)

    dp = updater.dispatcher

    # Please check state diagram
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING: [MessageHandler(Filters.regex('^Search$'), search),
                       MessageHandler(Filters.regex('^History$'), history)],

            SEARCH: [MessageHandler(Filters.all, result)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)
    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()