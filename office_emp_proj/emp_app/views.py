from django.shortcuts import render,HttpResponse,get_object_or_404
from .models import Employee,Role,Department
from datetime import datetime
from django.db.models import Q
import matplotlib.pyplot as plt
import io
import urllib, base64
from django.db import OperationalError


# Create your views here.

def index(request):
    graph = department_graph()
    graph1 = role_graph()
    return render(request,'index.html',{'dept_graph': graph,'role_graph': graph1})


def department_graph():
    departments = Department.objects.all()
    dept_names = [dept.name for dept in departments]
    emp_count = [Employee.objects.filter(dept=dept).count() for dept in departments]
    plt.figure(figsize=(10, 5))
    plt.bar(dept_names, emp_count, color='skyblue')
    plt.xlabel('Department')
    plt.ylabel('Number of Employees')
    plt.title('Number of Employees per Department')
    plt.xticks()
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    graph = base64.b64encode(image_png)
    graph = graph.decode('utf-8')
    return graph
    

def role_graph():
    roles = Role.objects.all()
    role_names = [role.name for role in roles]
    emp_count = [Employee.objects.filter(role=role).count() for role in roles]

    plt.figure(figsize=(10, 5))
    plt.bar(role_names, emp_count, color='lightgreen')
    plt.xlabel('Role')
    plt.ylabel('Number of Employees')
    plt.title('Number of Employees per Role')
    plt.xticks(rotation=20)
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    graph = base64.b64encode(image_png)
    graph = graph.decode('utf-8')
    return graph
    

def all_emp(request):
    emps = Employee.objects.all()
    context = {
        'emps': emps
    }
    print(context)
    return render(request,'all_emp.html',context)

def add_emp(request):
    if request.method == 'POST':
        try:
            # Process form data
            first_name = request.POST['first_name']
            last_name = request.POST['last_name']
            salary = int(request.POST['salary'])
            bonus = int(request.POST['bonus'])
            phone = int(request.POST['phone'])
            dept_name = request.POST['dept'].strip()
            role_name = request.POST['role'].strip()

            # Fetch Department and Role objects
            dept = get_object_or_404(Department, name=dept_name)
            role = get_object_or_404(Role, name=role_name)

            # Create and save new Employee
            new_emp = Employee(
                first_name=first_name,
                last_name=last_name,
                salary=salary,
                bonus=bonus,
                phone=phone,
                dept=dept,
                role=role,
                hire_date=datetime.now()
            )
            new_emp.save()
            return HttpResponse('Employee Added')

        except OperationalError as e:
            return HttpResponse(f'Database error: {e}')

        except ValueError as e:
            return HttpResponse(f'Error processing request: {e}')
    
    elif request.method =='GET':
        return render(request,'add_emp.html')
    else:
        return HttpResponse('Invalid Request')
    
def remove_emp(request,emp_id=0):
    if emp_id:
        try:
            emp_to_be_remove = Employee.objects.get(id=emp_id)
            emp_to_be_remove.delete()
            return HttpResponse('Employee Removed')
        except:
            return HttpResponse('Employee Not Found')
         
    emps = Employee.objects.all()
    context = {
        'emps': emps
    }
    return render(request,'remove_emp.html',context)

def filter_emp(request):
    if request.method == 'POST':
        name = request.POST['name']
        dept = request.POST['dept']
        role = request.POST['role']
        emps = Employee.objects.all()
        if name:
            emps = emps.filter(Q(first_name__icontains=name) | Q(last_name__icontains=name))
        if dept:
            emps = emps.filter(dept__name__icontains =  dept)
        if role:
            emps = emps.filter(role__name__icontains = role)
        
        context = {
            'emps': emps
        }
        return render(request,'all_emp.html',context)
    
    elif request.method == 'GET':
        return render(request,'filter_emp.html')
    else:
        return HttpResponse('Invalid Request')