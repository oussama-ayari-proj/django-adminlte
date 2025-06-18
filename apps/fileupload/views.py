from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
import pandas as pd
import os
import json
from django.http import JsonResponse
from django.conf import settings
import io

# Global temporary storage for file data (in a real app, you'd use a more robust solution)
file_storage = {}

def upload_file(request):
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        
        file_extension = os.path.splitext(uploaded_file.name)[1].lower()
        
        try:
            file_stats = {
                'name': uploaded_file.name,
                'size': uploaded_file.size,
                'type': uploaded_file.content_type
            }
            
            if file_extension == '.csv':
                df = pd.read_csv(io.StringIO(uploaded_file.read().decode('utf-8')))
                file_data = df.head(10).to_dict('records')
                
                # Update statistics
                file_stats.update({
                    'rows': len(df),
                    'columns': len(df.columns),
                    'column_names': df.columns.tolist(),
                    'data_types': df.dtypes.astype(str).to_dict(),
                    'missing_values': df.isnull().sum().to_dict()
                })
                
            elif file_extension == '.xlsx' or file_extension == '.xls':
                df = pd.read_excel(uploaded_file)
                file_data = df.head(10).to_dict('records') 
                
                file_stats.update({
                    'rows': len(df),
                    'columns': len(df.columns),
                    'column_names': df.columns.tolist(),
                    'data_types': df.dtypes.astype(str).to_dict(),
                    'missing_values': df.isnull().sum().to_dict(),
                    'sheets': pd.ExcelFile(uploaded_file).sheet_names,
                    'type': 'Fichier Excel'
                })                
            elif file_extension == '.json':
                json_data = json.loads(uploaded_file.read().decode('utf-8'))
                
                if isinstance(json_data, list):
                    df = pd.DataFrame(json_data)
                    file_data = json_data[:10]
                    
                    file_stats.update({
                        'rows': len(df),
                        'columns': len(df.columns),
                        'column_names': df.columns.tolist(),
                        'data_types': df.dtypes.astype(str).to_dict(),
                        'missing_values': df.isnull().sum().to_dict(),
                        'type': 'Tableau JSON'
                    })
                else:
                    file_data = json_data
                    file_stats.update({
                        'structure': 'Objet JSON imbriqué',
                        'top_level_keys': list(json_data.keys()),
                        'type': 'Objet JSON imbriqué'
                    })
                
            else:
                try:
                    file_content = uploaded_file.read().decode('utf-8')
                    file_data = {'content': file_content[:1000]}
                    file_stats.update({
                        'characters': len(file_content),
                        'lines': file_content.count('\n') + 1,
                        'type': 'Fichier texte'
                    })
                except UnicodeDecodeError:
                    file_data = {'error': 'Type de fichier binaire non pris en charge pour l\'aperçu'}
                    file_stats.update({
                        'binary': True,
                        'type': 'Fichier binaire'
                    })
            
            file_storage[uploaded_file.name] = {
                'file_data': file_data,
                'file_stats': file_stats
            }
            
            return redirect('fileupload:upload_success', file_name=uploaded_file.name)
        except Exception as e:
            return render(request, 'fileupload/upload.html', {'error': str(e)})
            
    return render(request, 'fileupload/upload.html')

def upload_success(request, file_name):
    file_data = {}
    file_stats = {}
    
    if file_name in file_storage:
        file_data = file_storage[file_name]['file_data']
        file_stats = file_storage[file_name]['file_stats']
        
    context = {
        'file_name': file_name,
        'file_data': file_data,
        'file_stats': file_stats
    }
    return render(request, 'fileupload/upload_success.html', context)
