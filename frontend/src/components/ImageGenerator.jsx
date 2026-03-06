import React, { useState } from 'react';
import { api } from '../services/api';

export function ImageGenerator() {
  const [prompt, setPrompt] = useState('');
  const [size, setSize] = useState('1024x1024');
  const [quality, setQuality] = useState('standard');
  const [style, setStyle] = useState('vivid');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [generatedImages, setGeneratedImages] = useState([]);

  const handleGenerate = async () => {
    if (!prompt.trim()) {
      setError('Please enter a prompt');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const result = await api.generateImage(prompt, {
        model: 'dall-e-3',
        size,
        quality,
        style
      });

      if (result.data && result.data.length > 0) {
        const newImages = result.data.map((img, index) => ({
          id: Date.now() + index,
          url: img.url,
          revisedPrompt: img.revised_prompt,
          originalPrompt: prompt,
          size,
          quality,
          style,
          createdAt: new Date().toLocaleString()
        }));
        setGeneratedImages([...newImages, ...generatedImages]);
      }
    } catch (err) {
      setError(err.message || 'Failed to generate image');
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey && !isLoading) {
      e.preventDefault();
      handleGenerate();
    }
  };

  const handleClearHistory = () => {
    setGeneratedImages([]);
  };

  const handleDownload = async (image) => {
    try {
      // If URL is a data URL (base64), convert to blob
      if (image.url.startsWith('data:')) {
        const response = await fetch(image.url);
        const blob = await response.blob();
        const blobUrl = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = blobUrl;
        link.download = `generated-image-${image.id}.png`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(blobUrl);
      } else {
        // For regular URLs, fetch and download
        const response = await fetch(image.url);
        const blob = await response.blob();
        const blobUrl = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = blobUrl;
        link.download = `generated-image-${image.id}.png`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(blobUrl);
      }
    } catch (err) {
      // Fallback: open in new tab
      window.open(image.url, '_blank');
    }
  };

  return (
    <div className="image-generator-layout">
      {/* Left side - Image Gallery */}
      <div className="image-gallery-panel">
        {error && (
          <div className="image-error">
            {error}
            <button onClick={() => setError(null)} className="dismiss-btn">×</button>
          </div>
        )}

        <div className="image-gallery">
          {isLoading && (
            <div className="image-loading">
              <div className="spinner"></div>
              <p>Generating your image...</p>
            </div>
          )}
          
          {generatedImages.map((image) => (
            <div key={image.id} className="image-card">
              <button 
                className="download-btn-corner" 
                onClick={() => handleDownload(image)}
                title="Download image"
              >
                📥
              </button>
              <div className="image-wrapper">
                <img src={image.url} alt={image.originalPrompt} />
              </div>
              <div className="image-info">
                <p className="image-prompt">{image.originalPrompt}</p>
                {image.revisedPrompt && image.revisedPrompt !== image.originalPrompt && (
                  <p className="revised-prompt">{image.revisedPrompt}</p>
                )}
                <p className="image-meta">
                  <span>{image.size}</span> • <span>{image.quality}</span> • <span>{image.style}</span> • <span>{image.createdAt}</span>
                </p>
              </div>
            </div>
          ))}
          
          {!isLoading && generatedImages.length === 0 && (
            <div className="empty-gallery">
              <p>🎨 No images generated yet</p>
              <p>Enter a prompt and click "Generate" to create your first image!</p>
            </div>
          )}
        </div>
      </div>

      {/* Right side - Controls */}
      <div className="image-controls-panel">
        <h3>Image Generator</h3>
        
        <div className="control-group">
          <label>Prompt</label>
          <textarea
            className="image-prompt-input"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Describe the image you want to generate..."
            disabled={isLoading}
            rows={4}
          />
        </div>
        
        <div className="control-group">
          <label>Size</label>
          <select value={size} onChange={(e) => setSize(e.target.value)} disabled={isLoading}>
            <option value="1024x1024">1024×1024 (Square)</option>
            <option value="1792x1024">1792×1024 (Landscape)</option>
            <option value="1024x1792">1024×1792 (Portrait)</option>
          </select>
        </div>
        
        <div className="control-group">
          <label>Quality</label>
          <select value={quality} onChange={(e) => setQuality(e.target.value)} disabled={isLoading}>
            <option value="standard">Standard</option>
            <option value="hd">HD</option>
          </select>
        </div>
        
        <div className="control-group">
          <label>Style</label>
          <select value={style} onChange={(e) => setStyle(e.target.value)} disabled={isLoading}>
            <option value="vivid">Vivid</option>
            <option value="natural">Natural</option>
          </select>
        </div>
        
        <button 
          className="generate-btn" 
          onClick={handleGenerate} 
          disabled={isLoading || !prompt.trim()}
        >
          {isLoading ? 'Generating...' : '✨ Generate Image'}
        </button>
        
        {generatedImages.length > 0 && (
          <button className="clear-history-btn" onClick={handleClearHistory}>
            🗑️ Clear History ({generatedImages.length})
          </button>
        )}
      </div>
    </div>
  );
}