import React from 'react'
import PropTypes from 'prop-types'
import Table from 'react-bootstrap/Table'
import OrderCancelConfirm from './OrderCancelConfirm'
import { displayNumber } from '../utils'

const Orderbook = (props) => {

  const renderLevels = () => {
    const { data } = props
    console.log(data)
    return data.map(level => {
      return level.orders.map(order => {
        return (
          <tr key={order.id}>
            <td>{displayNumber(order.price, 4)}</td>
            <td>{displayNumber(order.quantity, 0)}</td>
            <td>{displayNumber(order.leave_qty, 0)}</td>
            <td><OrderCancelConfirm order={order}/></td>
          </tr>
        )
      })
    })
  }

  return (
    <Table striped bordered hover>
      <thead>
        <tr>
          <th>Price</th>
          <th>Quantity</th>
          <th>Leave Qty</th>
          <th>Cancel</th>
        </tr>
      </thead>
      <tbody>
        {renderLevels()}
      </tbody>
    </Table>
  )
}

Orderbook.propTypes = {
  data: PropTypes.array.isRequired
}

export default Orderbook