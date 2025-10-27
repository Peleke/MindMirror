import MintVoucherForm from './MintVoucherForm'

export default function VouchersAdminPage() {
  return (
    <div className="max-w-3xl mx-auto p-6">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-semibold">Vouchers</h1>
        <a href="/admin" className="text-sm text-gray-600 hover:text-gray-800">Back to Dashboard</a>
      </div>
      <p className="text-sm text-gray-600 mb-4">Mint a voucher for testing or customer support. Sends an email with the code and redeem link.</p>
      <MintVoucherForm />
    </div>
  )
}


