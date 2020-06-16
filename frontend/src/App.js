import React, { useState, useEffect } from 'react'
import Page from './components/Page'
import OrderCreateForm from './components/OrderCreateForm'
import ActionBar from './components/ActionBar'
import Orderbook from './components/Orderbook'
import Row from 'react-bootstrap/Row'
import Col from 'react-bootstrap/Col'
import './App.css'
import initializeWebSocket from './ws'

function App() {

  const [ orderBook, setOrderBook ] = useState({buy: [], sell: []})

  const onWsMessage = (msg) => {
    const msgData = JSON.parse(msg.data)
    switch (msgData.type) {
      case 'orderbook_data':
        setOrderBook(msgData.data)
        break
      default:
          break
    }
  }

  useEffect(() => {
    initializeWebSocket({onMessage: onWsMessage})
  }, [])

  const [ showCreateForm, setShowCreateForm ] = useState(false)

  const getOrderBookData = (side) => {
    if (side === 'buy') {
      return orderBook.buy
    } else if (side === 'sell') {
      return orderBook.sell
    }
  }

  return (
    <div className="App">
      <Page>
        <Row className='mt-3 mb-5'>
          <Col xs={12}>
            <ActionBar setShowCreateForm={setShowCreateForm}/>
          </Col>
        </Row>
        <Row>
          <Col xs={12} lg={6}>
            <h3>Buy Book</h3>
            <Orderbook data={getOrderBookData('buy')}/>
          </Col>
          
          <Col xs={12} lg={6}>
            <h3>Sell Book</h3>
            <Orderbook data={getOrderBookData('sell')}/>
          </Col>
        </Row>
        <OrderCreateForm show={showCreateForm} setShow={setShowCreateForm}/>
      </Page>
    </div>
  );
}

export default App;
