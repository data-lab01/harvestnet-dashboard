import { useEffect, useState, useRef } from 'react';

export const useWebSocket = (farmId: string) => {
  const [lastMessage, setLastMessage] = useState<any>(null);
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  
  // WebSocket URL - backend remains on port 8000
  const WS_URL = `ws://localhost:8000/ws/${farmId}`;
  
  useEffect(() => {
    const ws = new WebSocket(WS_URL);
    wsRef.current = ws;
    
    ws.onopen = () => {
      console.log('WebSocket connected to HarvestNet backend');
      setIsConnected(true);
    };
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setLastMessage(data);
    };
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
    
    ws.onclose = () => {
      console.log('WebSocket disconnected');
      setIsConnected(false);
      
      // Attempt to reconnect after 3 seconds
      setTimeout(() => {
        console.log('Attempting to reconnect...');
      }, 3000);
    };
    
    return () => {
      ws.close();
    };
  }, [WS_URL]);
  
  const sendMessage = (data: any) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(data));
    }
  };
  
  return { lastMessage, sendMessage, isConnected };
};