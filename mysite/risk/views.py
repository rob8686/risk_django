from django.shortcuts import render, redirect
import yfinance as yf
import pandas as pd
from .forms import FundForm, PositionForm, SecurityForm
from .models import Security, Position, Fund
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import FundSerializer
from .risk_functions import get_yf_data, calc_liquidity, calc_performance
from datetime import datetime
# from django.contrib.auth import login, logout, authenticate


def index(request):
    fund_list = Fund.objects.all()
    context = {'fund_list': fund_list, 'user': str(request.user)}
    return render(request, 'risk/index.html', context)


def create(request):
    context = {}

    form = FundForm(request.POST or None)

    if form.is_valid():
        form.save()
        return redirect('risk:index')

    context['form'] = form
    return render(request, "risk/create.html", context)


def position_create(request):
    context = {}

    # make a copy of the post request so it can be altered
    updated_request = request.POST.copy()
    securities = Security.objects.all()
    form = PositionForm(updated_request or None, initial={'quantity': 6667})
    form.fields['fund'].initial = 'ABC UCITS'
    ticker = form['security'].value()

    if request.method == 'POST':

        ticker_list = list((securities.values_list('ticker', flat=True)))

        # If the ticker entered in the form is already an existing Security then change the ticker
        # in the form to the index of the Security in the Security list so the form references
        # a Security object rather than a string. Else set the form value to '0'.
        if ticker in ticker_list:
            updated_request.update({'security': str(ticker_list.index(ticker) + 1)})
        else:
            updated_request.update({'security': '0'})

        # Create Security if doesn't exist
        if int(form['security'].value()) == 0:

            yf_ticker = yf.Ticker(ticker)
            ticker_info = yf_ticker.info

            # check if ticker is valid
            if len(ticker_info) > 3:
                security = Security.objects.create(
                    name=ticker_info['longName'], ticker=ticker, 
                    sector=ticker_info['sector'],industry=ticker_info['industry'],
                    asset_class=ticker_info['quoteType'], currency=ticker_info['currency'])
                    
                ticker_list = list((securities.values_list('ticker', flat=True)))
                updated_request.update({'security': str(ticker_list.index(ticker) + 1)})

        if form.is_valid():
            instance = form.save(commit=False)
            closing_price = yf.Ticker(ticker).history(period="1d")['Close']
            closing_price.index = closing_price.index.strftime('%Y/%m/%d')
            instance.last_price = closing_price.item()
            instance.price_date = datetime.strptime(closing_price.index[0],'%Y/%m/%d')
            form.save()
            return redirect('risk:index')

    context['form'] = form

    return render(request, "risk/position_create.html", context)


def security_create(request):
    context = {}

    form = SecurityForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('risk:index')

    context['form'] = form
    return render(request, "risk/security_create.html", context)


def fund_positions(request, fund_name):
    print(fund_name)
    positions = Position.objects.filter(fund__name=fund_name)
    context = {'fund_positions': positions}
    print(context)
    #print(request.session[fund_name])
    return render(request, "risk/fund_positions.html", context)


@api_view(['GET'])
def get_hist_data_REST(request):
    #print(fund_name)
    #positions = Position.objects.filter(fund__name=fund_name)
    # fund = Fund.objects.filter(name=fund_name)
    # print(fund[0].Positions.all())
    #ticker_string = ''
    #for position in positions:
    #    print(position)
    #    ticker_string = ticker_string + str(position) + ' '

    request.session.set_expiry(0)
    #print('Ticker String')
    #print(ticker_string)
    #yf_data = get_yf_data(ticker_string)
    #print(yf_data)
    #request.session[fund_name] = yf_data.to_json(orient="split")
    # request.session['fav_color'] = 'blue'
    # print(request.session['fav_color'])
    #print(request.session[fund_name])
    #context = {'hist_data': request.session[fund_name]}
    # return render(request, "risk/get_hist_data.html", context)

    funds = Fund.objects.all()
    serializer = FundSerializer(funds, many=True)
    return Response(serializer.data)

    #return Response(context)

def get_hist_data(request, fund_name):
    positions = Position.objects.filter(fund__name=fund_name)
    print(list(positions.values_list('security_id','quantity')))
    #print(list(positions.values_list('quantity', flat=True))) 
    if positions.count() > 0:
        ticker_string = ''
        position_dict = {}

        for position in positions:
            position_dict[str(position)] = [position.quantity]
            ticker_string = ticker_string + str(position) + ' '

        request.session.set_expiry(0)

        yf_data = get_yf_data(ticker_string)
        yf_data.index = yf_data.index.strftime('%Y-%m-%d')

        performance = calc_performance(yf_data['Close'])
        print(performance)

        average_volumne = yf_data['Volume'].reset_index().mean().to_dict()
        
        for position in positions:
            ticker_series = yf_data['Close'][str(position)]
            last_price_index = ticker_series.last_valid_index()
            last_price_loc = ticker_series.index.get_loc(last_price_index)
            position.last_price = ticker_series[last_price_loc]
            position.price_date = datetime.strptime(last_price_index,'%Y-%m-%d')
            position.save()

        for ticker in average_volumne:
            if positions.count() > 1:
                position_dict[ticker].append(average_volumne[ticker])
            else:
                position_dict[ticker_string.strip()].append(average_volumne[ticker])

        liquidity_dict = {}
        for ticker in position_dict:
            quantity = float(position_dict[ticker][0])
            adv = float(position_dict[ticker][1])
            liquidity_dict[ticker] = calc_liquidity(quantity,adv) 
        
        context = {'hist_data': liquidity_dict}

        #request.session[fund_name] = '{"closing":' + yf_data['Close'].to_json(orient="split") +\
        #', "volume":' + yf_data['Volume'].to_json(orient="split") + '}'

        return render(request, "risk/get_hist_data.html", context)

    else:
        return redirect('risk:index')

