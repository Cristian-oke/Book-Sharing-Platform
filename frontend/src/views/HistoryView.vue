<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import { isAuthenticated, token } from '../auth'

const router = useRouter()
const BASE_URL = 'http://localhost:5000'

const isLoading = ref(true)
const sentRequests = ref([])
const receivedRequests = ref([])
const activeLoans = ref([])
const completedLoans = ref([])

//state pentru modal returnare
const isModalOpen = ref(false)
const selectedLoan = ref(null)
const reviewRating = ref(5)
const reviewComment = ref('')

const getAuthConfig = () => ({
  headers: { Authorization: `Bearer ${token.value}` }
})

const fetchHistoryData = async () => {
  if (!isAuthenticated.value) return
  try {
    isLoading.value = true
    const config = getAuthConfig() // Sau direct schema ta cu headers: Authorization

    const [sentRes, receivedRes, loansRes] = await Promise.all([
      axios.get(`${BASE_URL}/Book_Sharing/loans/my-outgoing-requests`, config).catch(() => ({ data: { outgoing_requests: [] } })),
      axios.get(`${BASE_URL}/Book_Sharing/loans/my-incoming-requests`, config).catch(() => ({ data: { incoming_requests: [] } })),
      axios.get(`${BASE_URL}/Book_Sharing/loans/my-loans`, config).catch(() => ({ data: { loans: [] } }))
    ])

    sentRequests.value = sentRes.data.outgoing_requests || []
    receivedRequests.value = receivedRes.data.incoming_requests || []    
    const allLoans = loansRes.data.loans || []
    activeLoans.value = allLoans.filter(l => l.status && l.status.toLowerCase() === 'activ')
    completedLoans.value = allLoans.filter(l => l.status && l.status.toLowerCase() === 'completed')

  } catch (err) {
    console.error("Eroare la încărcarea datelor istorice:", err)
  } finally {
    isLoading.value = false
  }
}

//modal control
const openReturnModal = (loan) => {
  selectedLoan.value = loan
  reviewRating.value = 5
  reviewComment.value = ''
  isModalOpen.value = true
}

const closeReturnModal = () => {
  isModalOpen.value = false
  selectedLoan.value = null
}

// Trimitere Review și finalizare retunrare
const submitReturn = async () => {
  try {
    const config = { headers: { Authorization: `Bearer ${token.value}` } }
    
    if (reviewRating.value > 0 && selectedLoan.value?.owner_id) {
      try {
        await axios.post(
          `${BASE_URL}/Book_Sharing/reviews/add-review/${selectedLoan.value.owner_id}`, 
          {
            rating: reviewRating.value,
            comment: reviewComment.value || ""
          }, 
          config
        )
      } catch (reviewErr) {
        console.warn("Nu s a putut adauga recenzia:", reviewErr.response?.data?.error || reviewErr.message)
      }
    }
    await axios.post(`${BASE_URL}/Book_Sharing/loans/return/${selectedLoan.value.id}`, {}, config)
    
    alert("Cartea a fost returnată cu succes proprietarului!")
    closeReturnModal()
    fetchHistoryData()
  } catch (err) {
    console.error("Eroare la returnare:", err)
    alert(err.response?.data?.error || "A apărut o eroare la procesarea returnării.")
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return '—'
  return new Date(dateStr).toLocaleDateString('ro-RO', { day: 'numeric', month: 'short', year: 'numeric' })
}

const translateStatus = (status) => {
  const translations = {
    'In asteptare': 'În așteptare ⏳',
    'Aprobat': 'Aprobată ✅',
    'Respins': 'Respinsă ❌',
    'activ': 'Activ 📖',
    'Completed': 'Finalizat 🎉'
  }
  return translations[status] || status
}

onMounted(() => {
  if (isAuthenticated.value) {
    fetchHistoryData()
  }
})
</script>

<template>
  <div class="history-container">
  <div v-if="!isAuthenticated" class="centered-auth-wrapper">
    <div class="simple-redirect-box">
      <h2>Nu ești autentificat</h2>
      <p>Trebuie să fii conectat pentru a accesa istoricul împrumuturilor</p>
      <button class="btn-simple-connect" @click="router.push('/login')">
        Conectează-te
      </button>
    </div>
  </div>

  <div v-else>
    
      <header class="history-header">
        <h1>Istoric</h1>
        <p>Urmărește cererile tale/împrumuturile finalizate și returnează cărțile din împrumuturile active</p>
      </header>

      <div v-if="isLoading" class="loading-state">
        <p>Se încarcă istoricul...</p>
      </div>

      <div v-else class="history-content">
        
        <section class="history-section">
          <h3>📖 Cărți pe care le-ai împrumutat și încă nu le-ai returnat</h3>
          <div v-if="activeLoans.length === 0" class="empty-msg">
            Nu ai niciun împrumut activ în acest moment.
          </div>
          <div v-else class="loans-grid">
            <div v-for="loan in activeLoans" :key="loan.id" class="loan-card">
              <div class="loan-card-info">
                <h4>{{ loan?.book_title || 'Carte Ștearsă' }}</h4>
                <p>de {{ loan?.book_author || 'Necunoscut' }}</p>
                <small>De la: <strong>{{ loan?.owner_name || 'Anonim' }}</strong></small>
                <small class="date">Împrumutat la: {{ formatDate(loan?.start_date) }}</small>
              </div>
              <button class="btn-return" @click="openReturnModal(loan)">Returnează cartea</button>
            </div>
          </div>
        </section>

        <section class="history-section">
          <h3>📥 Toate cererile primite</h3>
          <div v-if="receivedRequests.length === 0" class="empty-msg">
            Nu ai primit nicio cerere pentru cărțile tale.
          </div>
          <div v-else class="table-responsive">
            <table class="history-table">
              <thead>
                <tr>
                  <th>Carte</th>
                  <th>Cine cere</th>
                  <th>Dată cerere</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="req in receivedRequests" :key="req.request_id || req.id">
                  <td><strong>{{ req.book?.title || 'Carte Ștearsă' }}</strong></td>
                  <td>{{ req.requested_by?.name || 'Utilizator Anonim' }}</td>
                  <td>{{ formatDate(req.created_at) }}</td>
                  <td>
                    <span class="status-badge" :class="req.status ? req.status.replace(' ', '-').toLowerCase() : ''">
                      {{ translateStatus(req.status) }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <section class="history-section">
          <h3>📤 Toate cererile trimise de tine</h3>
          <div v-if="sentRequests.length === 0" class="empty-msg">
            Nu ai trimis nicio cerere de împrumut.
          </div>
          <div v-else class="table-responsive">
            <table class="history-table">
              <thead>
                <tr>
                  <th>Carte</th>
                  <th>Proprietar</th>
                  <th>Dată cerere</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="req in sentRequests" :key="req.request_id || req.id">
                  <td><strong>{{ req.book?.title || 'Carte Ștearsă' }}</strong></td>
                  <td>{{ req.book?.owner?.name || 'Anonim' }}</td>
                  <td>{{ formatDate(req.created_at) }}</td>
                  <td>
                    <span class="status-badge" :class="req.status ? req.status.replace(' ', '-').toLowerCase() : ''">
                      {{ translateStatus(req.status) }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <section class="history-section">
          <h3>🤝 Cărți pe care le-ai împrumutat și pe care le-ai returnat</h3>
          <div v-if="completedLoans.length === 0" class="empty-msg">
            Nu ai niciun împrumut finalizat.
          </div>
          <div v-else class="table-responsive">
            <table class="history-table">
              <thead>
                <tr>
                  <th>Carte</th>
                  <th>Proprietar</th>
                  <th>Dată început</th>
                  <th>Dată returnare</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="loan in completedLoans" :key="loan.id">
                  <td><strong>{{ loan?.book_title || 'Carte Ștearsă' }}</strong></td>
                  <td>{{ loan?.owner_name || 'Anonim' }}</td>
                  <td>{{ formatDate(loan?.start_date) }}</td>
                  <td>{{ formatDate(loan?.end_date) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

      </div>

      <div v-if="isModalOpen" class="modal-overlay" @click.self="closeReturnModal">
        <div class="modal-content">
          <h3>Returnare și Recenzie</h3>
          <p>
            Te-ai bucurat de cartea <strong>"{{ selectedLoan?.book_title }}"</strong>? 
            Lasă-i proprietarului ({{ selectedLoan?.owner_name || 'Anonim' }}) o recenzie!
          </p>
          
          <div class="form-group">
            <label>Rating proprietar:</label>
            <div class="star-rating-selector">
              <span 
                v-for="star in 5" 
                :key="star" 
                class="interactive-star"
                :class="{ 'filled': star <= reviewRating }"
                @click="reviewRating = star">★</span>
            </div>
          </div>

          <div class="form-group">
            <label2 for="review-comment">Mesaj (opțional):</label2>
            <textarea 
              id="review-comment" 
              v-model="reviewComment" 
              placeholder="Scrie câteva cuvinte despre experiența cu utilizatorul..."
              rows="3"
            ></textarea>
          </div>

          <div class="modal-buttons">
            <button class="btn-cancel" @click="closeReturnModal">Anulează</button>
            <button class="btn-submit-return" @click="submitReturn">Postează review și returnează cartea</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.centered-auth-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 50vh;
}

.simple-redirect-box {
  width: 100%;
  max-width: 400px;
  background: white;
  padding: 35px;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.06);
  border: 1px solid #eee;
  text-align: center;
}
.simple-redirect-box h2 { margin-bottom: 10px; color: #2c3e50; }
.simple-redirect-box p { color: #7f8c8d; font-size: 0.95rem; margin-bottom: 25px; line-height: 1.5; }
.btn-simple-connect { width: 100%; padding: 12px; background-color: #42b983; color: white; border: none; font-weight: bold; border-radius: 6px; cursor: pointer; font-size: 1rem; transition: background 0.2s; }
.btn-simple-connect:hover { background-color: #35495e; }
.loading-state {text-align: center; padding: 40px; font-weight: bold; color: #7f8c8d;}

.history-container {
  max-width: 1100px;
  margin: 0 auto;
  padding: 20px;
}

.history-header {
  margin-bottom: 30px;
  text-align: center;
}

.history-section {
  background: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  padding: 20px;
  margin-bottom: 25px;
}

.history-section h3 {
  margin-top: 0;
  margin-bottom: 15px;
  border-bottom: 2px solid #f0f0f0;
  padding-bottom: 8px;
  color: #333;
}

.empty-msg {
  color: #888;
  font-style: italic;
  padding: 10px 0;
}
.table-responsive {
  overflow-x: auto;
}

.history-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}

.history-table th, .history-table td {
  padding: 12px;
  border-bottom: 1px solid #eee;
  font-size: 0.9rem;
}

.history-table th {
  background: #fafafa;
  color: #555;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: bold;
  display: inline-block;
}
.status-badge.in-asteptare { background: #fff8e1; color: #ffb300; }
.status-badge.aprobat { background: #e8f5e9; color: #43a047; }
.status-badge.respins { background: #ffebee; color: #e53935; }
.status-badge.activ { background: #e3f2fd; color: #1e88e5; }
.status-badge.completed { background: #f5f5f5; color: #616161; }

.loans-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 15px;
}

.loan-card {
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  padding: 15px;
  display: flex;
  flex-direction: column;
  background: #fafafa;
}

.loan-card-info h4 {
  margin: 0 0 5px 0;
}
.loan-card-info p{margin-top:-2px}

.loan-card-info small {
  display: block;
  color: #666;
  margin: 2px 0;
}

.btn-return {
  margin-top: 15px;
  background-color: #1e88e5;
  color: white;
  border: none;
  padding: 8px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
  transition: background 0.2s;
}

.btn-return:hover {
  background-color: #1565c0;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 25px;
  border-radius: 8px;
  width: 100%;
  max-width: 450px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}
.modal-content h3 {
  text-align: center;
  margin-bottom: 15px;
}

.star-rating-selector {
  display: flex;
  gap: 8px;
  font-size: 2rem;
  margin: 10px 0;
}

.interactive-star {
  cursor: pointer;
  color: #ccc;
  transition: color 0.1s ease;
}

.interactive-star.filled {
  color: #ffca28;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  font-weight: bold;
  margin-bottom: -15px;
}
.form-group label2{
  display: block;
  font-weight: bold;
  margin-bottom: 5px;
}

.form-group textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
  resize: vertical;
}

.modal-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.btn-cancel {
  background: #eee;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}

.btn-submit-return {
  background: #43a047;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
}
</style>