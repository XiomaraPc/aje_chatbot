import React, { useState, useEffect, useRef } from 'react';
import { Send, Plus, MessageCircle, Bot } from 'lucide-react';

const API_BASE = 'http://localhost:5000';

const ChatBot = () => {
  const [userId] = useState('user_123');
  const [chats, setChats] = useState([]);
  const [currentChatId, setCurrentChatId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);
  const [selectedImage, setSelectedImage] = useState(null);

  useEffect(() => {
    loadChats();
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const loadChats = async () => {
    try {
      const response = await fetch(`${API_BASE}/chats/${userId}`);
      const data = await response.json();
      if (data) {
        setChats(data);
      }
    } catch (error) {
      console.error('Error loading chats:', error);
    }
  };

  const startNewChat = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE}/start-chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId })
      });
      const data = await response.json();

      if (data.chat_id) {
        setCurrentChatId(data.chat_id);
        setMessages([]);
        await loadChats();
      }
    } catch (error) {
      console.error('Error starting chat:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadChatMessages = async (chatId) => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE}/chat_messages/${userId}/${chatId}`);

      const data = await response.json();
      console.log(data)
      if (data) {
        setMessages(data);
        setCurrentChatId(chatId);
      }
    } catch (error) {
      console.error('Error loading messages:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleImageSelect = (e) => {
    const file = e.target.files[0];
    if (file && file.type === 'image/png') {
      setSelectedImage(file);
      sendImageMessage(file);
    } else {
      alert('Solo se permiten archivos PNG');
    }
  };
  const sendImageMessage = async (imageFile) => {
    if (!currentChatId || loading) return;

    try {
      setLoading(true);

      const imageMessage = {
        human: '[Imagen enviada]',
        ai: '',
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, imageMessage]);

      const reader = new FileReader();
      reader.onload = async () => {
        const base64Image = reader.result;

        const uploadResponse = await fetch(`${API_BASE}/upload-image`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            image: base64Image,
            user_id: userId,
            chat_id: currentChatId
          })
        });

        if (uploadResponse.ok) {
          const data = await uploadResponse.json();

          // ACTUALIZAR EL MENSAJE EXISTENTE
          setMessages(prev => {
            const newMessages = [...prev];
            newMessages[newMessages.length - 1] = {
              ...newMessages[newMessages.length - 1],
              ai: data.response
            };
            return newMessages;
          });
        }
        setLoading(false);
      };
      reader.readAsDataURL(imageFile);

    } catch (error) {
      console.error('Error enviando imagen:', error);
      setLoading(false);
    }
  };
  const formatMessage = (text) => {
    if (!text) return text;

    const lines = text.split('\n');
    const formatted = [];

    lines.forEach((line, index) => {
      if (line.startsWith('## ')) {
        formatted.push(
          <h3 key={index} style={{
            fontSize: '16px',
            fontWeight: '700',
            color: '#16a34a',
            margin: '16px 0 8px 0',
            borderBottom: '2px solid #dcfce7',
            paddingBottom: '4px'
          }}>
            {line.replace('## ', '').replace(/\*\*/g, '')}
          </h3>
        );
      }
      else if (line.includes('**')) {
        const parts = line.split(/(\*\*.*?\*\*)/);
        const formattedLine = parts.map((part, i) => {
          if (part.startsWith('**') && part.endsWith('**')) {
            return (
              <strong key={i} style={{ color: '#16a34a', fontWeight: '600' }}>
                {part.replace(/\*\*/g, '')}
              </strong>
            );
          }
          return part;
        });

        formatted.push(
          <p key={index} style={{
            margin: '4px 0',
            lineHeight: '1.5'
          }}>
            {formattedLine}
          </p>
        );
      }
      else if (line.startsWith('- ')) {
        formatted.push(
          <div key={index} style={{
            display: 'flex',
            alignItems: 'flex-start',
            margin: '4px 0',
            paddingLeft: '8px'
          }}>
            <span style={{
              color: '#16a34a',
              fontWeight: 'bold',
              marginRight: '8px',
              fontSize: '14px'
            }}>•</span>
            <span style={{ lineHeight: '1.5' }}>
              {line.replace('- ', '').replace(/\*\*/g, '')}
            </span>
          </div>
        );
      }
      else if (line.trim() === '') {
        formatted.push(<br key={index} />);
      }
      // Texto normal
      else if (line.trim() !== '') {
        formatted.push(
          <p key={index} style={{
            margin: '4px 0',
            lineHeight: '1.5'
          }}>
            {line.replace(/\*\*/g, '')}
          </p>
        );
      }
    });

    return <div>{formatted}</div>;
  };
  const sendMessage = async () => {
    if (!inputMessage.trim() || !currentChatId || loading) return;

    const userMessage = inputMessage;
    setInputMessage('');

    const userMessageObj = {
      human: userMessage,
      ai: '', // Vacío por ahora
      timestamp: new Date().toISOString()
    };
    setMessages(prev => [...prev, userMessageObj]);

    try {
      setLoading(true);
      const response = await fetch(`${API_BASE}/message`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId,
          chat_id: currentChatId,
          message: userMessage
        })
      });

      const data = await response.json();

      if (data.response) {
        setMessages(prev => {
          const newMessages = [...prev];
          newMessages[newMessages.length - 1] = {
            ...newMessages[newMessages.length - 1],
            ai: data.response
          };
          return newMessages;
        });
      }
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages(prev => {
        const newMessages = [...prev];
        newMessages[newMessages.length - 1] = {
          ...newMessages[newMessages.length - 1],
          ai: 'Error al enviar el mensaje. Intenta de nuevo.'
        };
        return newMessages;
      });
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div style={{
      display: 'flex',
      height: '100vh',
      backgroundColor: '#f5f5f5',
      fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
    }}>
      {/* Sidebar */}
      <div style={{
        width: '320px',
        backgroundColor: 'white',
        borderRight: '1px solid #e5e5e5',
        display: 'flex',
        flexDirection: 'column'
      }}>
        <div style={{
          padding: '16px',
          borderBottom: '1px solid #e5e5e5'
        }}>
          <button
            onClick={startNewChat}
            disabled={loading}
            style={{
              width: '100%',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '12px 16px',
              backgroundColor: '#16a34a',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: '500',
              opacity: loading ? 0.5 : 1,
              transition: 'background-color 0.2s'
            }}
            onMouseEnter={(e) => !loading && (e.target.style.backgroundColor = '#15803d')}
            onMouseLeave={(e) => e.target.style.backgroundColor = '#16a34a'}
          >
            <Plus size={20} />
            Nuevo Chat
          </button>
        </div>

        <div style={{
          flex: 1,
          overflowY: 'auto',
          padding: '16px'
        }}>
          <h3 style={{
            fontSize: '14px',
            fontWeight: '500',
            color: '#6b7280',
            margin: '0 0 12px 0'
          }}>Conversaciones</h3>
          {chats.length === 0 ? (
            <p style={{
              color: '#9ca3af',
              fontSize: '14px',
              margin: 0
            }}>No hay chats</p>
          ) : (
            <div style={{
              display: 'flex',
              flexDirection: 'column',
              gap: '8px'
            }}>
              {chats.map((chat) => {
                const chatId = chat.sk.split('#')[1];
                return (
                  <button
                    key={chat.sk}
                    onClick={() => loadChatMessages(chatId)}
                    style={{
                      width: '100%',
                      textAlign: 'left',
                      padding: '5px 12px',
                      background: currentChatId === chatId ? '#dcfce7' : 'none',
                      border: currentChatId === chatId ? '1px solid #86efac' : 'none',
                      borderRadius: '8px',
                      cursor: 'pointer',
                      transition: 'background-color 0.2s'
                    }}
                    onMouseEnter={(e) => currentChatId !== chatId && (e.target.style.backgroundColor = '#f9fafb')}
                    onMouseLeave={(e) => currentChatId !== chatId && (e.target.style.backgroundColor = 'transparent')}
                  >
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px'
                    }}>
                      <MessageCircle size={16} style={{ color: '#9ca3af' }} />
                      <div>
                        <p style={{
                          fontSize: '14px',
                          fontWeight: '500',
                          color: '#111827',
                          margin: 0,
                          whiteSpace: 'nowrap',
                          overflow: 'hidden',
                          textOverflow: 'ellipsis'
                        }}>
                          {chat.titulo || `Chat ${chatId}...`}
                        </p>
                        <p style={{
                          fontSize: '12px',
                          color: '#6b7280',
                          margin: 0
                        }}>
                        </p>
                      </div>
                    </div>
                  </button>
                );
              })}
            </div>
          )}
        </div>
      </div>

      {/* Chat Area */}
      <div style={{
        flex: 1,
        display: 'flex',
        flexDirection: 'column'
      }}>
        {/* Header */}
        <div style={{
          padding: '16px',
          borderBottom: '1px solid #e5e5e5',
          backgroundColor: 'white'
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '12px'
          }}>
            <div style={{
              width: '40px',
              height: '40px',
              borderRadius: '15px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              backgroundColor: 'white',
              padding: '4px'
            }}>
              <img
                src="./image.png"
                alt="AJE Group Logo"
                style={{
                  width: '100%',
                  height: '100%',
                  objectFit: 'contain'
                }}
              />
            </div>
            <div>
              <h1 style={{
                fontSize: '20px',
                fontWeight: '700',
                color: '#111827',
                margin: 0,
                fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
                letterSpacing: '-0.02em'
              }}>AJEBOT</h1>
              <p style={{
                fontSize: '14px',
                color: '#16a34a',
                margin: 0,
                fontWeight: '500'
              }}>Asistente oficial de AJE Group</p>
            </div>
          </div>
        </div>

        {/* Messages */}
        <div style={{
          flex: 1,
          overflowY: 'auto',
          padding: '16px',
          backgroundColor: '#f9fafb'
        }}>
          {!currentChatId ? (
            <div style={{
              height: '100%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <div style={{ textAlign: 'center' }}>
                <Bot size={48} style={{
                  margin: '0 auto 16px',
                  color: '#16a34a'
                }} />
                <h3 style={{
                  fontSize: '18px',
                  fontWeight: '600',
                  color: '#111827',
                  margin: '0 0 8px 0'
                }}>¡Hola! Soy AJEBOT</h3>
                <p style={{
                  color: '#6b7280',
                  margin: '0 0 16px 0',
                  lineHeight: 1.5
                }}>
                  Soy el asistente oficial de AJE Group. Puedo ayudarte con información sobre<br />
                  nuestra estrategia de internacionalización y productos.
                </p>
                <button
                  onClick={startNewChat}
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '8px',
                    padding: '12px 16px',
                    backgroundColor: '#16a34a',
                    color: 'white',
                    border: 'none',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    fontSize: '14px',
                    transition: 'background-color 0.2s'
                  }}
                  onMouseEnter={(e) => e.target.style.backgroundColor = '#15803d'}
                  onMouseLeave={(e) => e.target.style.backgroundColor = '#16a34a'}
                >
                  <Plus size={16} />
                  Iniciar conversación
                </button>
              </div>
            </div>
          ) : (
            <div style={{
              display: 'flex',
              flexDirection: 'column',
              gap: '16px'
            }}>
              {messages.map((message, index) => {
                const messagesArray = [];

                if (message.human && message.human.trim() !== '') {
                  messagesArray.push(
                    <div
                      key={`${index}-human`}
                      style={{
                        display: 'flex',
                        justifyContent: 'flex-end',
                        alignItems: 'flex-end',
                        gap: '8px',
                        marginBottom: '8px'
                      }}
                    >
                      <div style={{
                        maxWidth: '65%',
                        padding: '14px 18px',
                        borderRadius: '20px 20px 4px 20px',
                        backgroundColor: '#16a34a',
                        color: 'white',
                        boxShadow: '0 2px 8px rgba(22, 163, 74, 0.15)',
                        position: 'relative'
                      }}>
                        <p style={{
                          fontSize: '15px',
                          margin: '0 0 6px 0',
                          whiteSpace: 'pre-wrap',
                          lineHeight: 1.5,
                          fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
                          fontWeight: '400'
                        }}>{message.human}</p>
                        <p style={{
                          fontSize: '11px',
                          margin: 0,
                          color: 'rgba(255, 255, 255, 0.8)',
                          textAlign: 'right'
                        }}>
                          {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </p>
                      </div>
                      <div style={{
                        width: '32px',
                        height: '32px',
                        backgroundColor: '#f3f4f6',
                        borderRadius: '50%',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontSize: '14px',
                        fontWeight: '600',
                        color: '#374151',
                        flexShrink: 0
                      }}>
                        👤
                      </div>
                    </div>
                  );
                }

                // Mensaje del AI (si existe)
                if (message.ai && message.ai.trim() !== '') {
                  messagesArray.push(
                    <div
                      key={`${index}-ai`}
                      style={{
                        display: 'flex',
                        justifyContent: 'flex-start',
                        alignItems: 'flex-end',
                        gap: '8px',
                        marginBottom: '16px'
                      }}
                    >
                      <div style={{
                        width: '32px',
                        height: '32px',
                        borderRadius: '20px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        backgroundColor: 'white',
                        padding: '2px',
                        border: '1px solid #e5e7eb'
                      }}>
                        <img
                          src="./image.png"
                          alt="AJE"
                          style={{
                            width: '85%',
                            height: '80%',
                            objectFit: 'contain'
                          }}
                        />
                      </div>
                      <div style={{
                        maxWidth: '65%',
                        padding: '14px 18px',
                        borderRadius: '20px 20px 20px 4px',
                        backgroundColor: 'white',
                        color: '#1f2937',
                        boxShadow: '0 2px 8px rgba(0, 0, 0, 0.08)',
                        border: '1px solid #f3f4f6',
                        position: 'relative'
                      }}>
                        <p style={{
                          fontSize: '15px',
                          margin: '0 0 6px 0',
                          whiteSpace: 'pre-wrap',
                          lineHeight: 1.5,
                          fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
                          fontWeight: '400'
                        }}>{formatMessage(message.ai)}</p>
                        <p style={{
                          fontSize: '11px',
                          margin: 0,
                          color: '#9ca3af',
                          textAlign: 'right'
                        }}>
                          {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </p>
                      </div>
                    </div>
                  );
                }

                return messagesArray;
              })}
              {loading && (
                <div style={{
                  display: 'flex',
                  justifyContent: 'flex-start',
                  alignItems: 'flex-end',
                  gap: '8px'
                }}>
                  <div style={{
                    width: '40px',
                    height: '40px',
                    borderRadius: '10px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    backgroundColor: 'white',
                    padding: '4px'
                  }}>
                    <img
                      src="./image.png"
                      alt="AJE Group Logo"
                      style={{
                        width: '100%',
                        height: '100%',
                        objectFit: 'contain'
                      }}
                    />
                  </div>
                  <div style={{
                    backgroundColor: 'white',
                    padding: '14px 18px',
                    borderRadius: '20px 20px 20px 4px',
                    boxShadow: '0 2px 8px rgba(0, 0, 0, 0.08)',
                    border: '1px solid #f3f4f6'
                  }}>
                    <div style={{
                      display: 'flex',
                      gap: '4px',
                      padding: '4px 0'
                    }}>
                      <div style={{
                        width: '8px',
                        height: '8px',
                        backgroundColor: '#16a34a',
                        borderRadius: '50%',
                        animation: 'bounce 1.4s infinite ease-in-out'
                      }}></div>
                      <div style={{
                        width: '8px',
                        height: '8px',
                        backgroundColor: '#16a34a',
                        borderRadius: '50%',
                        animation: 'bounce 1.4s infinite ease-in-out',
                        animationDelay: '0.16s'
                      }}></div>
                      <div style={{
                        width: '8px',
                        height: '8px',
                        backgroundColor: '#16a34a',
                        borderRadius: '50%',
                        animation: 'bounce 1.4s infinite ease-in-out',
                        animationDelay: '0.32s'
                      }}></div>
                    </div>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Input */}
        {currentChatId && (
          <div style={{
            padding: '16px',
            backgroundColor: 'white',
            borderTop: '1px solid #e5e5e5'
          }}>
            <input
              type="file"
              accept="image/png"
              onChange={handleImageSelect}
              style={{ display: 'none' }}
              ref={fileInputRef}
            />
            <div style={{
              display: 'flex',
              gap: '12px',
              alignItems: 'flex-end'
            }}>
              <textarea
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Escribe tu pregunta sobre AJE Group..."
                style={{
                  flex: 1,
                  padding: '12px 16px',
                  border: '2px solid #e5e7eb',
                  borderRadius: '24px',
                  resize: 'none',
                  fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
                  fontSize: '14px',
                  outline: 'none',
                  transition: 'all 0.2s ease',
                  minHeight: '48px'
                }}
                onFocus={(e) => e.target.style.borderColor = '#16a34a'}
                onBlur={(e) => e.target.style.borderColor = '#e5e7eb'}
                rows="1"
                disabled={loading}
              />
              <button
                onClick={() => fileInputRef.current.click()}
                disabled={loading}
                style={{
                  padding: '5px',
                  backgroundColor: '#f3f4f6',
                  color: '#374151',
                  border: 'none',
                  borderRadius: '50%',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  width: '48px',
                  height: '48px',
                  opacity: loading ? 0.5 : 1,
                  fontSize: '25px',
                  lineHeight: '1'
                }}
              >
                📷
              </button>
              <button
                onClick={sendMessage}
                disabled={loading || !inputMessage.trim()}
                style={{
                  padding: '12px',
                  backgroundColor: '#16a34a',
                  color: 'white',
                  border: 'none',
                  borderRadius: '50%',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  opacity: (loading || !inputMessage.trim()) ? 0.5 : 1,
                  transition: 'all 0.2s ease',
                  width: '48px',
                  height: '48px'
                }}
                onMouseEnter={(e) => !loading && inputMessage.trim() && (e.target.style.backgroundColor = '#15803d')}
                onMouseLeave={(e) => e.target.style.backgroundColor = '#16a34a'}
              >
                <Send size={20} />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatBot;