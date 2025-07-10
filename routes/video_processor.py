from flask import Blueprint, request, jsonify
from flask_cors import CORS
import yt_dlp
import os
import tempfile
import json
from datetime import datetime

video_bp = Blueprint('video', __name__)
CORS(video_bp)

@video_bp.route('/process-video', methods=['POST'])
def process_video():
    """
    Processa um vídeo do YouTube para gerar cortes automáticos
    """
    try:
        data = request.get_json()
        youtube_url = data.get('url')
        
        if not youtube_url:
            return jsonify({'error': 'URL do YouTube é obrigatória'}), 400
        
        # Validar se é uma URL válida do YouTube
        if 'youtube.com' not in youtube_url and 'youtu.be' not in youtube_url:
            return jsonify({'error': 'URL inválida. Use uma URL do YouTube válida.'}), 400
        
        # Extrair informações do vídeo
        video_info = extract_video_info(youtube_url)
        
        # Gerar cortes sugeridos baseados na duração
        suggested_cuts = generate_suggested_cuts(video_info)
        
        return jsonify({
            'success': True,
            'video_info': video_info,
            'suggested_cuts': suggested_cuts,
            'message': 'Vídeo processado com sucesso!'
        })
        
    except Exception as e:
        return jsonify({'error': f'Erro ao processar vídeo: {str(e)}'}), 500

def extract_video_info(url):
    """
    Extrai informações do vídeo do YouTube usando yt-dlp
    """
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        
        return {
            'title': info.get('title', 'Título não disponível'),
            'duration': info.get('duration', 0),
            'description': info.get('description', '')[:500] + '...' if info.get('description') else '',
            'uploader': info.get('uploader', 'Canal não disponível'),
            'view_count': info.get('view_count', 0),
            'upload_date': info.get('upload_date', ''),
            'thumbnail': info.get('thumbnail', ''),
            'url': url
        }

def generate_suggested_cuts(video_info):
    """
    Gera sugestões de cortes baseadas na duração do vídeo
    """
    duration = video_info.get('duration', 0)
    title = video_info.get('title', '')
    
    cuts = []
    
    if duration > 0:
        # Para vídeos longos, sugerir múltiplos cortes de 30-60 segundos
        if duration > 300:  # Mais de 5 minutos
            # Corte do início (momento de hook)
            cuts.append({
                'start_time': 0,
                'end_time': 45,
                'title': f'Abertura - {title[:30]}...',
                'description': 'Momento inicial do vídeo, geralmente contém o hook principal',
                'viral_potential': 'Alto'
            })
            
            # Corte do meio (conteúdo principal)
            mid_point = duration // 2
            cuts.append({
                'start_time': mid_point - 30,
                'end_time': mid_point + 30,
                'title': f'Momento Principal - {title[:30]}...',
                'description': 'Parte central do vídeo com conteúdo principal',
                'viral_potential': 'Médio'
            })
            
            # Corte do final (conclusão/revelação)
            cuts.append({
                'start_time': duration - 60,
                'end_time': duration - 15,
                'title': f'Conclusão - {title[:30]}...',
                'description': 'Momento final com conclusão ou revelação',
                'viral_potential': 'Alto'
            })
        
        elif duration > 120:  # Entre 2-5 minutos
            # Corte único do melhor momento
            cuts.append({
                'start_time': 15,
                'end_time': 75,
                'title': f'Melhor Momento - {title[:30]}...',
                'description': 'Trecho mais interessante do vídeo',
                'viral_potential': 'Alto'
            })
        
        else:  # Vídeos curtos
            cuts.append({
                'start_time': 0,
                'end_time': min(60, duration - 5),
                'title': f'Vídeo Completo - {title[:30]}...',
                'description': 'Vídeo já é curto, usar quase completo',
                'viral_potential': 'Médio'
            })
    
    # Adicionar roteiros sugeridos para cada corte
    for i, cut in enumerate(cuts):
        cut['suggested_script'] = generate_script_for_cut(cut, video_info)
        cut['id'] = i + 1
    
    return cuts

def generate_script_for_cut(cut, video_info):
    """
    Gera um roteiro sugerido para narração do corte
    """
    title = video_info.get('title', '')
    
    scripts = [
        f"Você não vai acreditar no que aconteceu neste vídeo! {title[:50]}...",
        f"Isso vai mudar completamente sua perspectiva sobre...",
        f"O que você está prestes a ver é absolutamente incrível!",
        f"Prepare-se para ficar chocado com esta descoberta!",
        f"Isso é algo que 99% das pessoas não sabem!",
    ]
    
    # Escolher script baseado no tipo de corte
    if 'Abertura' in cut['title']:
        return scripts[0]
    elif 'Principal' in cut['title']:
        return scripts[1]
    elif 'Conclusão' in cut['title']:
        return scripts[2]
    else:
        return scripts[3]



