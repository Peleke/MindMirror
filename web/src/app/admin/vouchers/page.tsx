import MintVoucherForm from './MintVoucherForm'

export default function VouchersAdminPage() {
  return (
    <div className="max-w-3xl mx-auto p-6">
      <h1 className="text-2xl font-semibold mb-4">Vouchers</h1>
      <p className="text-sm text-gray-600 mb-4">Mint a voucher for testing or customer support. Sends an email with the code and redeem link.</p>
      <MintVoucherForm />
    </div>
  )
}


