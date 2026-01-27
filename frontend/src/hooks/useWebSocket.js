/**
 * Nexus AI - WebSocket Hook
 * React hook for real-time updates via WebSocket
 */

import { useState, useEffect, useCallback, useRef } from 'react';

const WS_URL = 'ws://localhost:8000/ws';

/**
 * WebSocket connection states
 */
export const ConnectionState = {
    CONNECTING: 'connecting',
    CONNECTED: 'connected',
    DISCONNECTED: 'disconnected',
    ERROR: 'error'
};

/**
 * WebSocket event types (match backend)
 */
export const EventType = {
    // Task events
    TASK_CREATED: 'task_created',
    TASK_STARTED: 'task_started',
    TASK_PROGRESS: 'task_progress',
    TASK_COMPLETED: 'task_completed',
    TASK_FAILED: 'task_failed',

    // Agent events
    AGENT_STARTED: 'agent_started',
    AGENT_PROGRESS: 'agent_progress',
    AGENT_COMPLETED: 'agent_completed',
    AGENT_ERROR: 'agent_error',
    AGENT_MESSAGE: 'agent_message',

    // System events
    CONNECTION_ESTABLISHED: 'connection_established',
    HEARTBEAT: 'heartbeat',
    ERROR: 'error'
};

/**
 * Custom hook for WebSocket connection and real-time updates
 * 
 * @param {string} token - JWT authentication token
 * @param {Object} options - Configuration options
 * @returns {Object} WebSocket state and methods
 */
export function useWebSocket(token, options = {}) {
    const {
        autoConnect = true,
        reconnect = true,
        reconnectAttempts = 5,
        reconnectInterval = 3000,
        onMessage = null,
        onConnect = null,
        onDisconnect = null,
        onError = null
    } = options;

    const [connectionState, setConnectionState] = useState(ConnectionState.DISCONNECTED);
    const [lastMessage, setLastMessage] = useState(null);
    const [messages, setMessages] = useState([]);

    const wsRef = useRef(null);
    const reconnectCountRef = useRef(0);
    const reconnectTimeoutRef = useRef(null);

    /**
     * Connect to WebSocket server
     */
    const connect = useCallback(() => {
        if (!token) {
            console.warn('WebSocket: No token provided');
            return;
        }

        if (wsRef.current?.readyState === WebSocket.OPEN) {
            console.log('WebSocket: Already connected');
            return;
        }

        setConnectionState(ConnectionState.CONNECTING);

        try {
            const ws = new WebSocket(`${WS_URL}?token=${token}`);
            wsRef.current = ws;

            ws.onopen = () => {
                console.log('🔌 WebSocket connected');
                setConnectionState(ConnectionState.CONNECTED);
                reconnectCountRef.current = 0;

                if (onConnect) {
                    onConnect();
                }
            };

            ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    setLastMessage(data);
                    setMessages(prev => [...prev.slice(-99), data]); // Keep last 100

                    if (onMessage) {
                        onMessage(data);
                    }
                } catch (e) {
                    console.error('WebSocket: Failed to parse message', e);
                }
            };

            ws.onerror = (error) => {
                console.error('❌ WebSocket error:', error);
                setConnectionState(ConnectionState.ERROR);

                if (onError) {
                    onError(error);
                }
            };

            ws.onclose = (event) => {
                console.log('🔌 WebSocket closed:', event.code, event.reason);
                setConnectionState(ConnectionState.DISCONNECTED);
                wsRef.current = null;

                if (onDisconnect) {
                    onDisconnect();
                }

                // Attempt reconnect
                if (reconnect && reconnectCountRef.current < reconnectAttempts) {
                    reconnectCountRef.current += 1;
                    console.log(`WebSocket: Reconnecting (${reconnectCountRef.current}/${reconnectAttempts})...`);

                    reconnectTimeoutRef.current = setTimeout(() => {
                        connect();
                    }, reconnectInterval);
                }
            };

        } catch (error) {
            console.error('WebSocket: Connection failed', error);
            setConnectionState(ConnectionState.ERROR);
        }
    }, [token, onConnect, onMessage, onDisconnect, onError, reconnect, reconnectAttempts, reconnectInterval]);

    /**
     * Disconnect from WebSocket server
     */
    const disconnect = useCallback(() => {
        if (reconnectTimeoutRef.current) {
            clearTimeout(reconnectTimeoutRef.current);
            reconnectTimeoutRef.current = null;
        }

        reconnectCountRef.current = reconnectAttempts; // Prevent reconnect

        if (wsRef.current) {
            wsRef.current.close(1000, 'Client disconnect');
            wsRef.current = null;
        }

        setConnectionState(ConnectionState.DISCONNECTED);
    }, [reconnectAttempts]);

    /**
     * Send a message to the server
     */
    const sendMessage = useCallback((action, data = {}) => {
        if (wsRef.current?.readyState !== WebSocket.OPEN) {
            console.warn('WebSocket: Not connected');
            return false;
        }

        try {
            wsRef.current.send(JSON.stringify({ action, ...data }));
            return true;
        } catch (error) {
            console.error('WebSocket: Send failed', error);
            return false;
        }
    }, []);

    /**
     * Subscribe to a task for updates
     */
    const subscribeToTask = useCallback((taskId) => {
        return sendMessage('subscribe_task', { task_id: taskId });
    }, [sendMessage]);

    /**
     * Unsubscribe from a task
     */
    const unsubscribeFromTask = useCallback((taskId) => {
        return sendMessage('unsubscribe_task', { task_id: taskId });
    }, [sendMessage]);

    /**
     * Send a ping to keep connection alive
     */
    const ping = useCallback(() => {
        return sendMessage('ping');
    }, [sendMessage]);

    /**
     * Clear message history
     */
    const clearMessages = useCallback(() => {
        setMessages([]);
        setLastMessage(null);
    }, []);

    // Auto connect on mount
    useEffect(() => {
        if (autoConnect && token) {
            connect();
        }

        return () => {
            disconnect();
        };
    }, [autoConnect, token, connect, disconnect]);

    // Heartbeat to keep connection alive
    useEffect(() => {
        if (connectionState !== ConnectionState.CONNECTED) return;

        const heartbeatInterval = setInterval(() => {
            ping();
        }, 30000);

        return () => clearInterval(heartbeatInterval);
    }, [connectionState, ping]);

    return {
        // State
        connectionState,
        isConnected: connectionState === ConnectionState.CONNECTED,
        lastMessage,
        messages,

        // Methods
        connect,
        disconnect,
        sendMessage,
        subscribeToTask,
        unsubscribeFromTask,
        ping,
        clearMessages
    };
}

/**
 * Hook for subscribing to a specific task's updates
 * 
 * @param {number} taskId - Task ID to subscribe to
 * @param {string} token - JWT authentication token
 * @returns {Object} Task events and connection state
 */
export function useTaskUpdates(taskId, token) {
    const [taskEvents, setTaskEvents] = useState([]);
    const [agentStatus, setAgentStatus] = useState({});

    const handleMessage = useCallback((message) => {
        if (message.task_id !== taskId) return;

        setTaskEvents(prev => [...prev, message]);

        // Track agent status
        if (message.event_type.startsWith('agent_')) {
            const agentName = message.data?.agent_name;
            if (agentName) {
                setAgentStatus(prev => ({
                    ...prev,
                    [agentName]: {
                        status: message.data?.status || message.event_type,
                        progress: message.data?.progress || 0,
                        message: message.data?.message,
                        timestamp: message.timestamp
                    }
                }));
            }
        }
    }, [taskId]);

    const { isConnected, connectionState, subscribeToTask, unsubscribeFromTask } = useWebSocket(token, {
        onMessage: handleMessage,
        onConnect: () => {
            if (taskId) {
                subscribeToTask(taskId);
            }
        }
    });

    // Subscribe when taskId changes
    useEffect(() => {
        if (isConnected && taskId) {
            subscribeToTask(taskId);
        }

        return () => {
            if (isConnected && taskId) {
                unsubscribeFromTask(taskId);
            }
        };
    }, [isConnected, taskId, subscribeToTask, unsubscribeFromTask]);

    // Clear events when task changes
    useEffect(() => {
        setTaskEvents([]);
        setAgentStatus({});
    }, [taskId]);

    return {
        isConnected,
        connectionState,
        taskEvents,
        agentStatus,
        latestEvent: taskEvents[taskEvents.length - 1] || null
    };
}

export default useWebSocket;
