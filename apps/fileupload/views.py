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
    if request.method == 'POST':
        file_categories = ['rh_file', 'rsa_file', 'lits_file', 'matrice_file', 'uf_file']
        uploaded_files = {}
        errors = []
        
        # Check if at least one file was uploaded
        has_files = any(request.FILES.get(category) for category in file_categories)
        
        if not has_files:
            return render(request, 'fileupload/upload.html', {
                'error': 'Veuillez sélectionner au moins un fichier à télécharger.'
            })
        
        # Process each file category
        for category in file_categories:
            uploaded_file = request.FILES.get(category)
            if uploaded_file:
                try:
                    file_extension = os.path.splitext(uploaded_file.name)[1].lower()
                    
                    file_stats = {
                        'name': uploaded_file.name,
                        'size': uploaded_file.size,
                        'type': uploaded_file.content_type,
                        'category': category.replace('_file', '').upper()
                    }
                    # If we have csv file
                    if file_extension == '.csv':
                        df = pd.read_csv(io.StringIO(uploaded_file.read().decode('utf-8')))
                        file_data = df.head(10).to_dict('records')
                        
                        # Update stats
                        file_stats.update({
                            'rows': len(df),
                            'columns': len(df.columns),
                            'column_names': df.columns.tolist(),
                            'data_types': df.dtypes.astype(str).to_dict(),
                            'missing_values': df.isnull().sum().to_dict()
                        })

                    # If we have Excel file  
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
                    # If we have JSON file
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
                    
                    # If we have Text file
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
                    
                    uploaded_files[category] = {
                        'file_data': file_data,
                        'file_stats': file_stats
                    }
                    
                except Exception as e:
                    errors.append(f"Erreur lors du traitement du fichier {category.replace('_file', '').upper()}: {str(e)}")
        
        if errors:
            return render(request, 'fileupload/upload.html', {
                'error': ' | '.join(errors)
            })
        
        # Store all uploaded files in global storage
        if not request.session.session_key:
            request.session.create()
        session_key = f"upload_session_{request.session.session_key}"
        file_storage[session_key] = uploaded_files
        
        return redirect('fileupload:upload_success_multiple', session_key=session_key)
            
    return render(request, 'fileupload/upload.html')

def upload_success_multiple(request, session_key):
    """Handle the success page for multiple file uploads"""
    uploaded_files = file_storage.get(session_key, {})
    
    context = {
        'uploaded_files': uploaded_files,
        'session_key': session_key
    }
    return render(request, 'fileupload/upload_success_multiple.html', context)
