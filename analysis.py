import numpy
import pandas
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.preprocessing import scale
from io import BytesIO
from PIL import Image
import csv
from sklearn.preprocessing import StandardScaler

DIR = "/etc/halo-session/"



def perform_pca(pseudo):

	complete = pandas.read_csv(f"{DIR}{pseudo}_stats.csv", delimiter=";").dropna()
	print(complete.head())
	print(complete)
	complete_numeric = complete.drop(columns=["map", "mode", "betrayals", "suicides"])
	scaler = StandardScaler()
	complete_numeric[complete_numeric.columns] = scaler.fit_transform(complete_numeric[complete_numeric.columns])
	print(complete_numeric.head())
	pca = PCA()
	pca.fit(complete_numeric)
	print(pca.explained_variance_ratio_)
	coord_pca = pca.transform(complete_numeric)

	n = complete_numeric.shape[0] # nb individus
	p = complete_numeric.shape[1] # nb variables
	eigval = (n-1) / n * pca.explained_variance_ # valeurs propres
	sqrt_eigval = numpy.sqrt(eigval) # racine carrée des valeurs propres
	corvar = numpy.zeros((p,p)) # matrice vide pour avoir les coordonnées
	for k in range(p):
		corvar[:,k] = pca.components_[k,:] * sqrt_eigval[k]
	# on modifie pour avoir un dataframe
	coordvar = pandas.DataFrame({'id': complete_numeric.columns, 'COR_1': corvar[:,0], 'COR_2': corvar[:,1]})

	fig, axes = plt.subplots(figsize = (6,6))
	fig.suptitle("Cercle des corrélations")
	axes.set_xlim(-1, 1)
	axes.set_ylim(-1, 1)
	print(coordvar)
	# Ajout des axes
	axes.axvline(x = 0, color = 'lightgray', linestyle = '--', linewidth = 1)
	axes.axhline(y = 0, color = 'lightgray', linestyle = '--', linewidth = 1)
	# Ajout des noms des variables
	for j in range(p):
		axes.text(coordvar["COR_1"][j],coordvar["COR_2"][j], coordvar["id"][j])
		axes.arrow(0, 0, coordvar["COR_1"][j], coordvar["COR_2"][j])
	# Ajout du cercle
	plt.gca().add_artist(plt.Circle((0,0),1,color='blue',fill=False))

	plt.savefig(f"{DIR}{pseudo}.png")
	image = Image.open(f"{DIR}{pseudo}.png")
	binary = BytesIO()
	image.save(binary, "PNG")
	binary.seek(0)
	return binary


def perform_pca_ind(pseudo, sup="map"):

	complete = pandas.read_csv(f"{DIR}{pseudo}_stats.csv", delimiter=";").dropna()
	print(complete.head())
	print(complete)
	
	# Sélection des colonnes numériques
	complete_numeric = complete.drop(columns=["map", "mode", "betrayals", "suicides"])
	
	# Centrer et mettre à l'échelle les données numériques
	scaler = StandardScaler()
	complete_numeric[complete_numeric.columns] = scaler.fit_transform(complete_numeric[complete_numeric.columns])
	print(complete_numeric.head())
	
	# Ajouter la variable "map" aux données numériques déjà centrées et mises à l'échelle
	
	# Appliquer PCA
	pca = PCA()
	pca.fit(complete_numeric)

	print(pca.explained_variance_ratio_)
	coord_pca = pca.transform(complete_numeric)


	# ... (le reste du code pour le cercle des corrélations reste inchangé)

	# Visualiser le graphe des individus avec la variable "map"
	fig, axes = plt.subplots(figsize=(10, 8))
	fig.suptitle(f"Graphe des individus de l'ACP avec la variable '{sup}'")
	
	axes.axvline(x = 0, color = 'lightgray', linestyle = '--', linewidth = 1)
	axes.axhline(y = 0, color = 'lightgray', linestyle = '--', linewidth = 1)

	_, unique_indices = numpy.unique(complete[sup], return_index=True)
	maps_array = complete[sup][numpy.sort(unique_indices)]
	# Utiliser une couleur différente pour chaque catégorie de la variable "map"
	complete_numeric[sup] = complete[sup]

	for m in maps_array:
		indices = complete_numeric[sup] == m
		axes.scatter(coord_pca[indices, 0], coord_pca[indices, 1], label=m, alpha=0.7)
	
	# Ajouter des annotations pour chaque point
	for i, score in enumerate(complete["score"]):
		axes.annotate(f"{score/complete['duration'][i]:.2f}", (coord_pca[i, 0], coord_pca[i, 1]), fontsize=10)
	
	# Ajouter une légende
	axes.legend()
	
	# Afficher le graphe

	# ... (le reste du code pour le cercle des corrélations reste inchangé)

	# Sauvegarder le cercle des corrélations
	plt.savefig(f"{DIR}{pseudo}_individus.png")

	image = Image.open(f"{DIR}{pseudo}_individus.png")
	binary = BytesIO()
	image.save(binary, "PNG")
	binary.seek(0)
	return binary

if __name__ == "__main__":
	from random import randint
	filename = f"{DIR}test_stats.csv"
	with open(filename, "w") as file:
		writer = csv.writer(file, delimiter=';')
		with open(filename, "w") as file:
				writer = csv.writer(file, delimiter=';')
				writer.writerow(["map", "mode", "kills", "deaths", "assists", "betrayals", "suicides", "max_killing_spree", "medals", "dmg_taken", "dmg_dealt", "shots_fired", "shots_hit", "shots_missed", "score", "duration"])
				writer.writerow(["Valhalla", "Husky Raid", randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50)])
				writer.writerow(["Valhalla", "Husky Raid", randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50)])
				writer.writerow(["Valhalla", "Husky Raid", randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50)])
				writer.writerow(["Valhalla", "Husky Raid", randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50)])
				writer.writerow(["Valhalla", "Husky Raid", randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50)])
				writer.writerow(["Valhalla", "Husky Raid", randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50)])
				writer.writerow(["Valhalla", "Husky Raid", randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50)])
				writer.writerow(["Valhalla", "Husky Raid", randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50)])
				writer.writerow(["Valhalla", "Husky Raid", randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50)])
				writer.writerow(["Valhalla", "Husky Raid", randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50)])
				writer.writerow(["Valhalla", "Husky Raid", randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50)])
				writer.writerow(["Valhalla", "Husky Raid", randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50)])
				writer.writerow(["Valhalla", "Husky Raid", randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50)])
				writer.writerow(["Valhalla", "Husky Raid", randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50)])
				writer.writerow(["Valhalla", "Husky Raid", randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50)])
				writer.writerow(["Valhalla", "Husky Raid", randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50)])
				writer.writerow(["Valhalla", "Husky Raid", randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50)])
				writer.writerow(["Valhalla", "Husky Raid", randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50)])
				writer.writerow(["Valhalla", "Husky Raid", randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50)])
				writer.writerow(["Valhalla", "Husky Raid", randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50)])
				writer.writerow(["Valhalla", "Husky Raid", randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50)])
				writer.writerow(["Valhalla", "Husky Raid", randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50)])
				writer.writerow(["Valhalla", "Husky Raid", randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50)])
				writer.writerow(["Valhalla", "Husky Raid", randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50), randint(5, 50)])
				
	perform_pca_ind("SirArthurias", "mode")
