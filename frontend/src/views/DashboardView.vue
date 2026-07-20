<script setup>
import { ref, onMounted ,computed} from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import { isAuthenticated, token } from '../auth'

const router = useRouter()
const BASE_URL = 'http://localhost:5000'
const currentView = ref('list')

//date utilizator logat
const myBooks = ref([])
const incomingRequests = ref([])
const outgoingRequests = ref([])
const isLoadingDashboard = ref(true)

//doar cererile in asteptare
const pendingIncomingRequests = computed(() => {
  return incomingRequests.value.filter(req => req.status === 'In asteptare')
})
const pendingOutgoingRequests = computed(() => {
  return outgoingRequests.value.filter(req => req.status === 'In asteptare')
})

const formErrors = ref([])
const formSuccess = ref('')

const currentBookId = ref(null) 
const title = ref('')
const author = ref('')
const isbn = ref('')
const description = ref('')
const status = ref('Buna') 
const availability = ref('Disponibila') 
const imageBase64 = ref('')

const getAuthConfig = () => ({
  headers: { Authorization: `Bearer ${token.value}` }
})

const fetchDashboardData = async () => {
  if (!isAuthenticated.value) return
  try {
    isLoadingDashboard.value = true
    const config = getAuthConfig()
    const booksRes = await axios.get(`${BASE_URL}/Book_Sharing/books/my-books`, config).catch(() => ({ data: { books: [] } }))
    const incomingRes = await axios.get(`${BASE_URL}/Book_Sharing/loans/my-incoming-requests`, config).catch(() => ({ data: [] }))
    const outgoingRes = await axios.get(`${BASE_URL}/Book_Sharing/loans/my-outgoing-requests`, config).catch(() => ({ data: [] }))
    
    myBooks.value = booksRes.data.books || []
    incomingRequests.value = incomingRes.data.incoming_requests || []
    outgoingRequests.value = outgoingRes.data.outgoing_requests || []
  } catch (err) {
    console.error("Eroare la încărcarea datelor:", err)
  } finally {
    isLoadingDashboard.value = false
  }
}

onMounted(() => {
  fetchDashboardData()
})

//incarcare imagine din PC sI transformare in base64
const handleImageUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    const reader = new FileReader()
    reader.onload = (e) => {
      imageBase64.value = e.target.result
    }
    reader.readAsDataURL(file)
  }
}

const resetForm = () => {
  currentBookId.value = null
  title.value = ''
  author.value = ''
  isbn.value = ''
  description.value = ''
  status.value = 'Buna'
  availability.value = 'Disponibila'
  imageBase64.value = ''
  formErrors.value = []
  formSuccess.value = ''
}

const openAddView = () => {
  resetForm()
  currentView.value = 'add'
}

//stergere carte
const handleDeleteBook = async (bookId, bookTitle) => {
  if (confirm(`Ești sigur că vrei să ștergi cartea "${bookTitle}"?`)) {
    try {
      await axios.delete(`${BASE_URL}/Book_Sharing/books/delete/${bookId}`, getAuthConfig())
      myBooks.value = myBooks.value.filter(book => book.id !== bookId)
      alert("Cartea a fost ștearsă cu succes!")
    } catch (error) {
      alert(error.response?.data?.error || "Nu s-a putut șterge cartea.")
    }
  }
}

const openEditView = (book) => {
  resetForm()
  currentBookId.value = book.id
  title.value = book.title
  author.value = book.author
  isbn.value = book.isbn || ''
  description.value = book.description || ''
  status.value = book.status || 'Buna'
  availability.value = book.availability || 'Disponibila'
  imageBase64.value = book.image_url || ''
  currentView.value = 'edit'
}

//procesare erori marshmallow
const handleFormBackendError = (error) => {
  formErrors.value = []
  if (error.response && error.response.data) {
    const data = error.response.data
    if (data.errors) {
      Object.keys(data.errors).forEach(field => {
        formErrors.value.push(`${field}: ${data.errors[field]}`)
      })
    } else if (data.error) {
      formErrors.value.push(data.error)
    }
  } else {
    formErrors.value.push("Eroare de conexiune la server.")
  }
}

//adaugare carte
const handleAddBook = async () => {
  try {
    formErrors.value = []
    const bookData = {
      title: title.value,
      author: author.value,
      isbn: isbn.value || null,
      description: description.value || null,
      status: status.value,
      availability: availability.value,
      image_url: imageBase64.value || null
    }
    await axios.post(`${BASE_URL}/Book_Sharing/books/add`, bookData, getAuthConfig())
   
    await fetchDashboardData()
    currentView.value = 'list'
  } catch (error) {
    handleFormBackendError(error)
  }
}

//eitare carte
const handleEditBook = async () => {
  try {
    formErrors.value = []
    const bookData = {
      title: title.value,
      author: author.value,
      isbn: isbn.value || null,
      description: description.value || null,
      status: status.value,
      availability: availability.value,
      image_url: imageBase64.value || null
    }
    await axios.put(`${BASE_URL}/Book_Sharing/books/edit/${currentBookId.value}`, bookData, getAuthConfig())
    
    await fetchDashboardData()
    currentView.value = 'list'
  } catch (error) {
    handleFormBackendError(error)
  } 
}

const handleRespondToRequest = async (requestId, decision) => {
  const actionText = decision === 'Aprobat' ? 'accepți' : 'respingi'
  if (confirm(`Ești sigur că vrei să ${actionText} această cerere?`)) {
    try {
      const config = getAuthConfig()
      //trimitere status (aprobat/respins)
      await axios.put(`${BASE_URL}/Book_Sharing/loans/request/${requestId}/respond`, { status: decision }, config)
      alert(`Cererea a fost procesată cu succes (${decision})!`)
      await fetchDashboardData() 
    } catch (error) {
      alert(error.response?.data?.error || "Eroare la trimiterea deciziei.")
    }
  }
}

</script>

<template>
  <div class="dashboard-container">
    
    <div v-if="!isAuthenticated" class="centered-auth-wrapper">
      <div class="simple-redirect-box">
        <h2>Nu ești autentificat</h2>
        <p>Trebuie să fii conectat pentru a avea acces la dashboard</p>
        <button class="btn-simple-connect" @click="router.push('/login')">
          Conectează-te
        </button>
      </div>
    </div>

    <div v-else>
      <div v-if="currentView === 'list'">
        <div class="dashboard-header">
          <h1>👋 Dashboard</h1>
          <button class="btn-add-main" @click="openAddView">➕ Adaugă o carte nouă</button>
        </div>
        
        <div v-if="isLoadingDashboard" class="loading">Se încarcă datele tale...</div>

        <div v-else class="dashboard-sections">
          
          <section class="dash-section">
            <h3>📚 Cărțile mele </h3>
            <div v-if="myBooks.length === 0" class="empty-list">Nu ai adăugat nicio carte încă.</div>
            <ul v-else class="book-list">
              <li v-for="book in myBooks" :key="book.id" class="book-item">
                <div class="book-info">
                  <img :src="book.image_url || '/default-image.jpg'" class="book-thumb" />
                  <div>
                    <strong>{{ book.title }}</strong>
                    <p>{{ book.author }}</p>
                    <span class="badge" :class="book.availability">{{ book.availability }}</span>
                    <span class="badge status-badge">{{ book.status }}</span>
                  </div>
                </div>
                <div class="book-actions">
                  <button class="btn-edit-action" @click="openEditView(book)">✏️ Editează</button>
                  <button class="btn-delete-action" @click="handleDeleteBook(book.id, book.title)">🗑️ Șterge</button>
                </div>
              </li>
            </ul>
          </section>

          <section class="dash-section">
          <h3>📥 Cereri active primite de la alții</h3>
          <div v-if="pendingIncomingRequests.length === 0" class="empty-list">
            Nu ai nicio cerere nouă în așteptare.
          </div>
          <ul v-else class="request-list" style="padding: 0; margin: 0;">
            <li v-for="req in pendingIncomingRequests" :key="req.request_id" class="request-item-box">
              <div class="request-text">
                👤 Utilizatorul <strong>{{ req.requested_by?.name }}</strong> (din {{ req.requested_by?.city }}) dorește cartea ta: <br>
                📚 <strong>{{ req.book?.title }}</strong> de {{ req.book?.author }}
              </div>
              <div class="request-actions-btns">
                <button class="btn-req-accept" @click="handleRespondToRequest(req.request_id, 'Aprobat')">✅ Acceptă</button>
                <button class="btn-req-reject" @click="handleRespondToRequest(req.request_id, 'Respins')">❌ Respinge</button>
                <button class="btn-req-profile" @click="router.push(`/user/${req.requested_by?.id}`)">👀 Vezi profil</button>
              </div>
            </li>
          </ul>
        </section>

        <section class="dash-section">
          <h3>📤 Cererile mele active trimise către alții</h3>
          <div v-if="pendingOutgoingRequests.length === 0" class="empty-list">
            Nu ai nicio cerere trimisă care se află în așteptare.
          </div>
          <ul v-else class="request-list" style="padding: 0; margin: 0;">
            <li v-for="req in pendingOutgoingRequests" :key="req.request_id" class="request-item-box">
              <div class="request-text">
                Ai cerut cartea <strong>{{ req.book?.title }}</strong> de la utilizatorul 👤 <strong>{{ req.book?.owner?.name }}</strong> ({{ req.book?.owner?.city }})
              </div>
              <div>
                Status cerere: <span class="badge status-badge">{{ req.status }}</span>
              </div>
            </li>
          </ul>
        </section>

        </div>
      </div>

      <div v-else class="form-container-box">
        <h2>{{ currentView === 'add' ? '➕ ADAUGĂ O CARTE ' : '✏️ Modifică Detaliile Cărții' }}</h2>
        
        <div v-if="formErrors.length > 0" class="alert error">
          <ul style="list-style: none; padding:0; margin:0;">
            <li v-for="(err, idx) in formErrors" :key="idx">⚠️ {{ err }}</li>
          </ul>
        </div>

        <form @submit.prevent="currentView === 'add' ? handleAddBook() : handleEditBook()">
          <div class="form-group">
            <label>Titlu carte *</label>
            <input v-model="title" type="text" required placeholder="Minim 3 caractere" />
          </div>

          <div class="form-group">
            <label>Autor *</label>
            <input v-model="author" type="text" required placeholder="Numele autorului" />
          </div>

          <div class="form-group">
            <label>Cod ISBN (Opțional)</label>
            <input v-model="isbn" type="text" placeholder="Ex: 978-3-16-148410-0" />
          </div>

          <div class="form-group">
            <label>Descriere / Detalii suplimentare</label>
            <textarea v-model="description" rows="3" placeholder="Mențiuni despre starea cărții, reguli predare..."></textarea>
          </div>

          <div class="form-row">
            <div class="form-group half">
              <label>Starea fizică a cărții</label>
              <select v-model="status">
                <option value="Noua">Nouă </option>
                <option value="Buna">Bună </option>
                <option value="Uzata">Uzată</option>
              </select>
            </div>

            <div class="form-group half">
              <label>Disponibilitate platformă</label>
              <select v-model="availability">
                <option value="Disponibila">Disponibilă</option>
                <option value="Imprumutata">Indisponibilă</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label>Imagine carte</label>
            <input type="file" @change="handleImageUpload" accept="image/*" />
            <div v-if="imageBase64" class="image-preview-wrapper">
              <p style="font-size: 0.8rem; margin-bottom: 5px;">Previzualizare imagine salvată:</p>
              <img :src="imageBase64" class="image-preview-img" />
            </div>
          </div>

          <div class="form-actions-zone">
            <button type="button" class="btn-cancel" @click="currentView = 'list'">Anulează</button>
            <button type="submit" class="btn-save">Salvează Cartea</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard-container { max-width: 1100px; margin: 0 auto; padding: 20px; }
.dashboard-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; }
.btn-add-main { background-color: #42b983; color: white; border: none; padding: 10px 20px; border-radius: 6px; font-weight: bold; cursor: pointer; }
.loading {text-align: center; padding: 40px; font-weight: bold; color: #7f8c8d;}

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

.dashboard-sections { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 25px; }
.dash-section { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); border: 1px solid #eee; }
.dash-section h3 { border-bottom: 2px solid #f4f6f8; padding-bottom: 10px; margin-top: 0; color: #2c3e50; }

.book-list { list-style: none; padding: 0; margin: 0; }
.book-item { display: flex; justify-content: space-between; align-items: center; padding: 12px 0; border-bottom: 1px solid #f4f6f8; }
.book-info { display: flex; align-items: center; gap: 12px; }
.book-thumb { width: 50px; height: 65px; object-fit: cover; border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
.book-info strong { font-size: 0.95rem; color: #2c3e50; }
.book-info p { margin: 2px 0; font-size: 0.85rem; color: #7f8c8d; }

.book-actions { display: flex; gap: 8px; }
.btn-edit-action { background: none; border: 1px solid #35495e; color: #35495e; padding: 5px 10px; border-radius: 4px; cursor: pointer; font-size: 0.85rem; font-weight: bold; }
.btn-edit-action:hover { background: #35495e; color: white; }
.btn-delete-action { background: none; border: 1px solid #e74c3c; color: #e74c3c; padding: 5px 10px; border-radius: 4px; cursor: pointer; font-size: 0.85rem; font-weight: bold; }
.btn-delete-action:hover { background: #e74c3c; color: white; }

.badge { font-size: 0.75rem; padding: 2px 6px; border-radius: 4px; font-weight: bold; margin-right: 5px; }
.badge.Disponibila { background-color: #e8f5e9; color: #2e7d32; }
.badge.Imprumutata { background-color: #ffebee; color: #c62828; }
.status-badge { background-color: #eaeaea; color: #555; }

/* Stiluri formulare */
.form-container-box { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.06); border: 1px solid #eee; }
.form-group { margin-bottom: 15px; display: flex; flex-direction: column; }
.form-group label { font-weight: bold; margin-bottom: 5px; font-size: 0.9rem; color: #34495e; }
.form-group input, .form-group select, .form-group textarea { padding: 10px; border: 1px solid #ccc; border-radius: 6px; font-size: 0.95rem; }
.form-row { display: flex; gap: 15px; }
.form-group.half { width: 50%; }

.image-preview-wrapper { margin-top: 10px; }
.image-preview-img { max-width: 120px; border-radius: 6px; border: 1px solid #ddd; padding: 4px; }

.form-actions-zone { display: flex; justify-content: flex-end; gap: 10px; margin-top: 20px; }
.btn-cancel { background: #95a5a6; color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; font-weight: bold; }
.btn-save { background: #42b983; color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; font-weight: bold; }

.empty-list { color: #95a5a6; font-style: italic; font-size: 0.9rem; margin-top: 15px; }
.alert.error { background: #ffebee; color: #c62828; padding: 12px; border-radius: 6px; margin-bottom: 20px; font-size: 0.9rem; font-weight: bold;}
.request-item-box {
  background: #fafbfc;
  padding: 15px;
  border-radius: 8px;
  border: 1px solid #e1e4e6;
  margin-bottom: 12px;
  list-style: none;
}
.request-text {
  font-size: 0.9rem;
  color: #2c3e50;
  line-height: 1.5;
  margin-bottom: 10px;
}
.request-actions-btns {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.request-actions-btns button {
  padding: 6px 12px;
  font-size: 0.8rem;
  font-weight: bold;
  border-radius: 4px;
  cursor: pointer;
  border: none;
}
.btn-req-accept { background-color: #2ecc71; color: white; }
.btn-req-accept:hover { background-color: #27ae60; }
.btn-req-reject { background-color: #e74c3c; color: white; }
.btn-req-reject:hover { background-color: #c0392b; }
.btn-req-profile { background-color: #3498db; color: white; }
.btn-req-profile:hover { background-color: #2980b9; }
</style>