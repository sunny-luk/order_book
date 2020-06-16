import ReconnectingWebSocket from 'reconnecting-websocket'


const initializeWebSocket = ({onOpen=null, onMessage=null, onClose=null}) => {
  console.log(process.env)
  const rws = new ReconnectingWebSocket(process.env.REACT_APP_WEBSOCKET_URL)
  rws.addEventListener('open', onOpen || (() => console.log('connected to ws')))

  rws.onmessage = onMessage || (({data}) => console.log(`message received: ${data}`))

  rws.addEventListener('close', onClose || (() => console.log('ws connection is closed')))

  return rws
}

export default initializeWebSocket