import React, { useState } from 'react'
import PropTypes from 'prop-types'
import Button from 'react-bootstrap/Button'
import Modal from 'react-bootstrap/Modal'
import Row from 'react-bootstrap/Row'
import Col from 'react-bootstrap/Col'
import { displayNumber } from '../utils'
import makeRequest from '../services/api'
import URLS from '../urls'

const OrderCancelConfirm = (props) => {

  const { order } = props

  const [ showModal, setShowModal ] = useState(false)
  const [ loading, setLoading ] = useState(false)

  const onHide = () => {
    setShowModal(false)
  }

  const onConfirm = () => {
    setLoading(true)
    makeRequest({
      method: 'POST',
      url: `${URLS.CANCEL_ORDER}${props.order.id}/`,
    }).then(data => {
        onHide()
        alert(data.data.msg)
      }
    ).catch(err => {
      setLoading(false)
      alert(err.response.data.msg)
    })
  }

  return (
    <>
      <Button variant='link' onClick={() => setShowModal(true)}>Cancel</Button>
      <Modal centered show={showModal} onHide={onHide}>
        <Modal.Body>
          <Row>
            <Col xs={12}><p>Please confirm if you would like to cancel below order</p></Col>
            <Col xs={12}>
              <ul>
                <li>Order Id: {order.order_id}</li>
                <li>Qty: {displayNumber(order.quantity, 0)}</li>
                <li>Leave Qty: {displayNumber(order.leave_qty, 0)}</li>
                <li>Accumulated amount: {displayNumber(order.acum_amount)}</li>
                <li>Avg filled price: {displayNumber(order.avg_fill_price)}</li>

              </ul>
            </Col>
            <Col xs={12} md={{span: 6, offset:3}} lg={{span: 4, offset: 4}}>
              <Button block variant='danger' onClick={onConfirm} disabled={loading}>{ loading ? 'Cancelling...' : 'Confirm'}</Button>
            </Col>
          </Row>
        </Modal.Body>
      </Modal>
    </>
  )
}

OrderCancelConfirm.propTypes = {
  order: PropTypes.object.isRequired
}

export default OrderCancelConfirm