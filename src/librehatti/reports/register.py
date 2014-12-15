from django.shortcuts import render

from django.http import HttpResponse

from librehatti.reports.forms import DailyReportForm
from librehatti.reports.forms import ConsultancyFunds
from librehatti.reports.forms import DateRangeSelectionForm
from librehatti.reports.forms import MonthYearForm
from librehatti.reports.forms import PaidTaxesForm

from datetime import datetime

from librehatti.catalog.request_change import request_notify
from librehatti.catalog.models import PurchaseOrder
from librehatti.catalog.models import Bill
from librehatti.catalog.models import PurchasedItem
from librehatti.catalog.models import Category
from librehatti.catalog.models import TaxesApplied
from librehatti.catalog.models import Surcharge

from librehatti.suspense.models import SuspenseOrder
from librehatti.suspense.models import Transport
from librehatti.suspense.models import TaDa
from librehatti.suspense.models import SuspenseClearance

from librehatti.voucher.models import CalculateDistribution
from librehatti.voucher.models import VoucherId


from django.db.models import Sum

from django.contrib.auth.decorators import login_required


@login_required
def daily_report_result(request):
    """
    This view is used to display the daily report registers
    """ 
    if request.method == 'POST':
        if 'button1' in request.POST:
            form = DailyReportForm(request.POST)
            date_form = DateRangeSelectionForm(request.POST)
            if form.is_valid() and date_form.is_valid():
                start_date = request.POST['start_date']
                end_date = request.POST['end_date']
                mode_of_payment = request.POST['mode_of_payment']
                list_of_report = []
                purchase_order = PurchaseOrder.objects.filter(date_time__range=\
                    (start_date,end_date)).filter(mode_of_payment=\
                    mode_of_payment).values('date_time','id')
                for date_value in purchase_order:
                    bill_object = Bill.objects.filter\
                    (purchase_order_id = date_value['id']).\
                    values('grand_total',\
                    'purchase_order__voucherid__purchase_order_of_session',\
                    'purchase_order__date_time',\
                    'purchase_order__buyer__first_name',\
                    'purchase_order__buyer__last_name',\
                    'purchase_order__buyer__customer__user__customer__address__street_address',\
                    'purchase_order__buyer__customer__user__customer__address__city').distinct()
                    list_of_report.append(bill_object)
                sum = 0
                for temp_var in list_of_report:
                    for total in temp_var:
                        sum = sum + total['grand_total']
                request_status = request_notify()
                return render(request,'reports/daily_report_result.html',\
                {'list_of_report':list_of_report,'sum':sum,'request':request_status})
            else:
                form = DailyReportForm(request.POST)
                date_form = DateRangeSelectionForm(request.POST)
                request_status = request_notify()
                return render(request,'reports/daily_report_form.html', \
                {'form':form,'date_form':date_form,'request':request_status})
    else:
        form = DailyReportForm()
        date_form = DateRangeSelectionForm()
        request_status = request_notify()
        return render(request,'reports/daily_report_form.html', \
        {'form':form,'date_form':date_form,'request':request_status}) 

@login_required
def consultancy_funds_report(request):
    """
    It generates the report which lists all 
    the Consultancy Funds for the Material
    selected and the in the entered Time Span.
    """
    if request.method == 'POST':
        if 'button1' in request.POST:
            form = ConsultancyFunds(request.POST)
            date_form = DateRangeSelectionForm(request.POST)
            if form.is_valid() and date_form.is_valid():
                category = request.POST['sub_category']
                start_date = request.POST['start_date']
                end_date = request.POST['end_date']
                purchase_item = PurchasedItem.objects.\
                filter(purchase_order__date_time__range=(start_date, end_date),\
                	item__category=category).values\
                ('purchase_order__voucherid__purchase_order_of_session',\
                 'purchase_order__date_time',\
                 'purchase_order__buyer__first_name',\
                 'purchase_order__buyer__last_name',\
                 'purchase_order__buyer__customer__title',\
                 'purchase_order__buyer__customer__user__customer__address__street_address',\
                 'purchase_order__buyer__customer__user__customer__address__city',\
                 'purchase_order__voucherid__session_id__calculatedistribution__consultancy_asset').distinct()
                category_name = Category.objects.filter(id=category).values('name')
                for a in category_name:
                	category_value = a['name']
                sum = PurchasedItem.objects.filter(\
                    purchase_order__date_time__range=(start_date,end_date),\
                    item__category=category).\
                aggregate(Sum('purchase_order__voucherid__session_id__calculatedistribution__consultancy_asset')).\
                get('purchase_order__voucherid__session_id__calculatedistribution__consultancy_asset__sum', 0.00)
                request_status = request_notify()
                return render(request, 'reports/consultancy_funds_result.html', {'purchase_item':
    	            purchase_item,'start_date':start_date, 'end_date':end_date,
    	            'sum':sum, 'category_name':category_value,\
    	            'request':request_status})
            else:
                form = ConsultancyFunds(request.POST)
                date_form = DateRangeSelectionForm(request.POST)
                request_status = request_notify()
                return render(request,'reports/consultancy_funds_form.html', \
                {'form':form,'date_form':date_form,'request':request_status})
    else:
        form = ConsultancyFunds()
        request_status = request_notify()
        date_form = DateRangeSelectionForm()
        return render(request,'reports/consultancy_funds_form.html', \
        {'form':form,'date_form':date_form,'request':request_status}) 

@login_required
def tds_report_result(request):
    """
    This view is used to display the TDS report registers
    """ 
    if request.method == 'POST':
        if 'button1' in request.POST:
            form = DateRangeSelectionForm(request.POST)
            if form.is_valid():
                start_date = request.POST['start_date']
                end_date = request.POST['end_date']
                purchase_order = PurchaseOrder.objects.filter(date_time__range=\
                    (start_date,end_date)).values('date_time','id')
                list_of_bill = []
                for date_value in purchase_order:
                        bill_object = Bill.objects.filter\
                        (purchase_order_id = date_value['id']).\
                        values('purchase_order__voucherid__purchase_order_of_session',\
                        'purchase_order__date_time',\
                        'purchase_order__buyer__first_name',\
                        'purchase_order__buyer__last_name',\
                        'purchase_order__buyer__customer__user__customer__address__street_address',\
                        'purchase_order__buyer__customer__user__customer__address__city',
                        'totalplusdelivery','amount_received','purchase_order__tds','grand_total'\
                        ).distinct()
                        list_of_bill.append(bill_object)  
                list_of_taxes = []
                for temp_var in purchase_order:
                    taxes_object = TaxesApplied.objects.filter(\
                        purchase_order__date_time__range=(start_date,end_date)).\
                    values('surcharge','tax')
                    list_of_taxes.append(taxes_object)
                tds_list = zip(list_of_bill,list_of_taxes)
                totalplusdel = 0
                amountreceived = 0
                purchaseordertds = 0
                grandtotal = 0
                for temp_var in list_of_bill:
                    for bill_object_var in temp_var:
                        totalplusdel = totalplusdel + bill_object_var['totalplusdelivery']
                        amountreceived = amountreceived + bill_object_var['amount_received']
                        purchaseordertds = purchaseordertds + bill_object_var['purchase_order__tds']
                        grandtotal = grandtotal + bill_object_var['grand_total'] 
                servicetax = 0
                Heducationcess = 0
                educationcess = 0
                for temp_var in list_of_taxes:
                    for taxes_object_var in temp_var:
                        if taxes_object_var['surcharge'] == 1:
                            servicetax = servicetax + taxes_object_var['tax']
                        elif taxes_object_var['surcharge'] == 3:
                            Heducationcess = Heducationcess + taxes_object_var['tax']
                        else:
                            educationcess = educationcess + taxes_object_var['tax']    
                request_status = request_notify()
                return render(request,'reports/tds_report_result.html',\
                {'tds_list':tds_list,'request':request_status,\
                'totalplusdel':totalplusdel,'amountreceived':amountreceived\
                ,'purchaseordertds':purchaseordertds,'grandtotal':grandtotal\
                ,'servicetax':servicetax,'Heducationcess':Heducationcess,\
                'educationcess':educationcess,'start_date':start_date,\
                'end_date':end_date})
            else:
                form = DateRangeSelectionForm(request.POST)
                request_status = request_notify()
                return render(request,'reports/tds_report_form.html', \
                {'form':form,'request':request_status})
    else:
        form = DateRangeSelectionForm()
        request_status = request_notify()
        return render(request,'reports/tds_report_form.html', \
        {'form':form,'request':request_status}) 

@login_required
def payment_register(request):
    """
    This view is used to display the payment registers
    """ 
    if request.method == 'POST':
        if 'button1' in request.POST:
            form = DateRangeSelectionForm(request.POST)
            if form.is_valid():
                start_date = request.POST['start_date']
                end_date = request.POST['end_date']
                purchase_order = PurchaseOrder.objects.filter\
                (date_time__range=(start_date,end_date)).values(\
                    'date_time','id')
               
                list_of_bill = []
                for date_value in purchase_order:
                        bill_object = Bill.objects.\
                        filter(purchase_order_id = date_value['id']).\
                        values('purchase_order__voucherid__purchase_order_of_session',\
                        'purchase_order__date_time',\
                        'purchase_order__buyer__first_name',\
                        'purchase_order__buyer__last_name',\
                        'purchase_order__buyer__customer__user__customer__address__street_address',\
                        'purchase_order__buyer__customer__user__customer__address__city',
                        'totalplusdelivery','purchase_order__tds','amount_received'\
                        ,'purchase_order__buyer__customer__user__email',\
                        'purchase_order__buyer__customer__telephone',\
                        'purchase_order__buyer__customer__company').distinct()
                list_of_bill.append(bill_object)  
                list_of_taxes = []
                for temp_var in purchase_order:
                    taxes_object = TaxesApplied.objects.filter(\
                        purchase_order__date_time__range=(start_date,end_date)).\
                    values('surcharge','tax')
                    list_of_taxes.append(taxes_object)
                for date_value in purchase_order:
                        Category = Bill.objects.\
                        filter(purchase_order_id = date_value['id']).\
                        values('purchase_order__purchaseditem__item__category__name')
                list_of_material = []
                for material_name in Category:
                    material =str((material_name['purchase_order__purchaseditem__item__category__name']+","))
                    list_of_material.append(material)
                material_list = "".join(str(x) for x in list_of_material)   
                payment_register_list = zip(list_of_bill,list_of_taxes)
                totalplusdel = 0
                amountreceived = 0
                purchaseordertds = 0
                grandtotal = 0
                for temp_var in list_of_bill:
                    for bill_object_var in temp_var:
                        totalplusdel = totalplusdel + bill_object_var['totalplusdelivery']
                        purchaseordertds = purchaseordertds + bill_object_var['purchase_order__tds']
                        amountreceived = amountreceived + bill_object_var['amount_received'] 
                servicetax = 0
                Heducationcess = 0
                educationcess = 0
                for temp_var in list_of_taxes:
                    for taxes_object_var in temp_var:
                        if taxes_object_var['surcharge'] == 1:
                            servicetax = servicetax + taxes_object_var['tax']
                        elif taxes_object_var['surcharge'] == 3:
                            Heducationcess = Heducationcess + taxes_object_var['tax']
                        else:
                            educationcess = educationcess + taxes_object_var['tax']    
                request_status = request_notify()
                return render(request,'reports/payment_register_result.html',\
                {'payment_register_list':payment_register_list,'request':request_status,\
                'totalplusdel':totalplusdel,'amountreceived':amountreceived\
                ,'purchaseordertds':purchaseordertds,\
                'servicetax':servicetax,'Heducationcess':Heducationcess,\
                'educationcess':educationcess,'start_date':start_date,\
                'end_date':end_date,'list_of_material':material_list})
            else:
                form = DateRangeSelectionForm(request.POST)
                request_status = request_notify()
                return render(request,'reports/payment_register_form.html', \
                {'form':form,'request':request_status})
    else:
        form = DateRangeSelectionForm()
        request_status = request_notify()
        return render(request,'reports/payment_register_form.html', \
        {'form':form,'request':request_status})


@login_required
def suspense_clearance_register(request):
    """
    This view is used to display the suspense clearance registers
    """
    if request.method == 'POST':
        form = DateRangeSelectionForm(request.POST)
        if form.is_valid():
            start_date = request.POST['start_date']
            end_date = request.POST['end_date']
            suspenseorder = SuspenseOrder.objects.values('voucher',\
                'session_id', 'purchase_order', 'purchase_order__date_time',\
                'purchase_order__buyer__first_name',\
                'purchase_order__buyer__last_name',\
                'purchase_order__buyer__customer__title',\
                'purchase_order__buyer__customer__address__street_address',\
                'purchase_order__buyer__customer__address__city',\
                'purchase_order__buyer__customer__address__pin',\
                'purchase_order__buyer__customer__address__province',\
                'purchase_order__voucherid__purchase_order_of_session').\
            filter(is_cleared=1,\
            purchase_order__date_time__range=(start_date,end_date))
            result = []
            temp = []
            for suspense in suspenseorder:
                temp.append(suspense['voucher'])
                temp.append(suspense['purchase_order__date_time'])
                temp.append(suspense[\
                    'purchase_order__voucherid__purchase_order_of_session'])
                if suspense['purchase_order__buyer__first_name']:
                    if suspense[\
                    'purchase_order__buyer__customer__address__pin'] == None:
                        address = suspense['purchase_order__buyer__first_name']\
                        + suspense['purchase_order__buyer__last_name']\
                        + ', ' +\
                        suspense[\
                        'purchase_order__buyer__customer__address__street_address']\
                        + ', ' + \
                        suspense[\
                        'purchase_order__buyer__customer__address__city']\
                        + ', ' + \
                        suspense[\
                        'purchase_order__buyer__customer__address__province']
                    else:
                        address = suspense['purchase_order__buyer__first_name'] +\
                        suspense['purchase_order__buyer__last_name'] +\
                        ', ' +\
                        suspense[\
                        'purchase_order__buyer__customer__address__street_address']\
                        + ', ' + \
                        suspense[\
                        'purchase_order__buyer__customer__address__city']\
                        + ', ' + \
                        suspense[\
                        'purchase_order__buyer__customer__address__province']
                else:
                    if suspense[\
                    'purchase_order__buyer__customer__address__pin'] == None:
                        address =\
                        suspense['purchase_order__buyer__customer__title']\
                        + ', ' +\
                        suspense[\
                        'purchase_order__buyer__customer__address__street_address']\
                        + ', ' + \
                        suspense[\
                        'purchase_order__buyer__customer__address__city']\
                        + ', ' + \
                        suspense[\
                        'purchase_order__buyer__customer__address__province']
                    else:
                        address =\
                        suspense['purchase_order__buyer__customer__title'] +\
                        ', ' +\
                        suspense[\
                        'purchase_order__buyer__customer__address__street_address']\
                        + ', ' + \
                        suspense[\
                        'purchase_order__buyer__customer__address__city']\
                        + ', ' + \
                        suspense[\
                        'purchase_order__buyer__customer__address__province']
                temp.append(address)
                voucherid = VoucherId.objects.values(\
                    'purchase_order__purchaseditem__item__category__name').\
                filter(voucher_no=suspense['voucher'],\
                    session_id=suspense['session_id'])[0]
                temp.append(voucherid[\
                    'purchase_order__purchaseditem__item__category__name'])
                caldistribute = CalculateDistribution.objects.values(\
                    'college_income_calculated', 'admin_charges_calculated',\
                    'consultancy_asset', 'development_fund', 'total').get(voucher_no=\
                    suspense['voucher'], session_id=suspense['session_id'])
                temp.append(caldistribute['college_income_calculated'])
                temp.append(caldistribute['admin_charges_calculated'])
                temp.append(caldistribute['consultancy_asset'])
                temp.append(caldistribute['development_fund'])
                try:
                    transport = Transport.objects.values('total').get(voucher_no=\
                        suspense['voucher'], session_id=suspense['session_id'])
                    trans_value = transport['total']
                    temp.append(trans_value)
                except:
                    trans_value = 0
                    temp.append(trans_value)
                try:
                    tada = TaDa.objects.values('tada_amount').get(voucher_no=\
                        suspense['voucher'], session=suspense['session_id'])
                    tada_value = tada['tada_amount']
                    temp.append(tada_value)
                except:
                    tada_value = 0
                    temp.append(tada_value)
                suspensecl = SuspenseClearance.objects.values(\
                    'work_charge', 'labour_charge', 'car_taxi_charge',\
                    'boring_charge_external', 'boring_charge_internal').get(\
                    voucher_no=suspense['voucher'],\
                    session_id=suspense['session_id'])
                other_charges = suspensecl['labour_charge'] +\
                suspensecl['car_taxi_charge'] +\
                suspensecl['boring_charge_external']
                temp.append(suspensecl['work_charge'])
                temp.append(other_charges)
                temp.append(suspensecl['boring_charge_internal'])
                grand_total = caldistribute['total'] + trans_value + tada_value\
                + suspensecl['work_charge'] + other_charges +\
                suspensecl['boring_charge_internal']
                temp.append(grand_total)
                result.append(temp)
                temp = []
            request_status = request_notify()
            return render(request,'reports/suspense_clearance_result.html',\
            {'result':result, 'request':request_status})
        else:
            form = DateRangeSelectionForm()
            request_status = request_notify()
            return render(request,'reports/suspense_clearance_form.html', \
            {'form':form,'request':request_status})
    else:
        form = DateRangeSelectionForm()
        request_status = request_notify()
        return render(request,'reports/suspense_clearance_form.html', \
        {'form':form,'request':request_status})


@login_required
def monthly_register(request):
    """
    This view is used to display the monthly registers
    """
    if request.method == 'POST':
        form = MonthYearForm(request.POST)
        data_form = PaidTaxesForm(request.POST)
        if form.is_valid() and data_form.is_valid:
            month = request.POST['month']
            year = request.POST['year']
            service = int(request.POST['paid_service_tax'])
            education = int(request.POST['paid_education_tax'])
            highereducation = int(request.POST['paid_higher_education_tax'])
            service_tax = 0
            education_tax = 0
            heducation_tax = 0
            total = 0
            totalplustax = 0
            surcharge = Surcharge.objects.values('value').filter(\
                taxes_included=1)[0]
            voucherid = VoucherId.objects.values('purchase_order_of_session',\
                'purchase_order', 'purchase_order__date_time',\
                'purchase_order__bill__totalplusdelivery',\
                'purchase_order__bill__grand_total',\
                'purchase_order__buyer__first_name',\
                'purchase_order__buyer__last_name',\
                'purchase_order__buyer__customer__title',\
                'purchase_order__buyer__customer__address__street_address',\
                'purchase_order__buyer__customer__address__city',\
                'purchase_order__buyer__customer__address__pin',\
                'purchase_order__buyer__customer__address__province').\
            filter(purchase_order__date_time__month=month,\
                purchase_order__date_time__year=year)
            temp = []
            result = []
            i=0
            for value in voucherid:
                temp.append(value['purchase_order_of_session'])
                temp.append(value['purchase_order__date_time'])
                if value['purchase_order__buyer__first_name']:
                    if value[\
                    'purchase_order__buyer__customer__address__pin'] == None:
                        address = value['purchase_order__buyer__first_name']\
                        + value['purchase_order__buyer__last_name']\
                        + ', ' +\
                        value[\
                        'purchase_order__buyer__customer__address__street_address']\
                        + ', ' + \
                        value[\
                        'purchase_order__buyer__customer__address__city']\
                        + ', ' + \
                        value[\
                        'purchase_order__buyer__customer__address__province']
                    else:
                        address = value['purchase_order__buyer__first_name'] +\
                        value['purchase_order__buyer__last_name'] +\
                        ', ' +\
                        value[\
                        'purchase_order__buyer__customer__address__street_address']\
                        + ', ' + \
                        value[\
                        'purchase_order__buyer__customer__address__city']\
                        + ', ' + \
                        value[\
                        'purchase_order__buyer__customer__address__province']
                else:
                    if value[\
                    'purchase_order__buyer__customer__address__pin'] == None:
                        address =\
                        + value['purchase_order__buyer__customer__title']\
                        + ', ' +\
                        value[\
                        'purchase_order__buyer__customer__address__street_address']\
                        + ', ' + \
                        value[\
                        'purchase_order__buyer__customer__address__city']\
                        + ', ' + \
                        value[\
                        'purchase_order__buyer__customer__address__province']
                    else:
                        address =\
                        value['purchase_order__buyer__customer__title'] +\
                        ', ' +\
                        value[\
                        'purchase_order__buyer__customer__address__street_address']\
                        + ', ' + \
                        value[\
                        'purchase_order__buyer__customer__address__city']\
                        + ', ' + \
                        value[\
                        'purchase_order__buyer__customer__address__province']
                temp.append(address)
                temp.append(value['purchase_order__bill__totalplusdelivery'])
                total = total+value['purchase_order__bill__totalplusdelivery']
                taxesapplied = TaxesApplied.objects.values('tax').filter(\
                    purchase_order=value['purchase_order'])
                for taxvalue in taxesapplied:
                    temp.append(taxvalue['tax'])
                    if i == 0:
                        service_tax = service_tax + taxvalue['tax']
                        i = i + 1
                    elif i == 1:
                        education_tax = education_tax + taxvalue['tax']
                        i = i + 1
                    else:
                        heducation_tax = heducation_tax + taxvalue['tax']
                        i = 0
                temp.append(value['purchase_order__bill__grand_total'])
                totalplustax = totalplustax +\
                value['purchase_order__bill__grand_total']
                result.append(temp)
                temp = []
            total_taxes = service_tax + education_tax + heducation_tax
            servicenotpaid = service_tax - service
            educationnotpaid = education_tax - education
            heducationnotpaid = heducation_tax - highereducation
            total_taxes_not_paid = servicenotpaid + educationnotpaid +\
            heducationnotpaid
            request_status = request_notify()
            return render(request,'reports/monthly_report.html',\
            {'result':result, 'request':request_status, 'surcharge':surcharge,\
            'month':month, 'year':year, 'total':total,\
            'totalplustax':totalplustax, 'service_tax':service_tax,\
            'education_tax':education_tax, 'heducation_tax':heducation_tax,\
            'total_taxes':total_taxes, 'servicenotpaid':servicenotpaid,\
            'educationnotpaid':educationnotpaid, 'heducationnotpaid':\
            heducationnotpaid, 'total_taxes_not_paid':total_taxes_not_paid,\
            'service':service, 'education':education, 'highereducation':\
            highereducation})
        else:
            form = MonthYearForm()
            data_form = PaidTaxesForm()
            request_status = request_notify()
            return render(request,'reports/monthly_form.html', \
            {'form':form, 'data_form':data_form, 'request':request_status})
    else:
        form = MonthYearForm()
        data_form = PaidTaxesForm()
        request_status = request_notify()
        return render(request,'reports/monthly_form.html', \
        {'form':form, 'data_form':data_form, 'request':request_status})