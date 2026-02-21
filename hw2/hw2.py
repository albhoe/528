from google.cloud import storage
from bs4 import BeautifulSoup
import numpy as np
import os

if not os.path.exists("link_matrix.npy"):
    #Opens the cloud bucket
    storage_client = storage.Client()
    bucket = storage_client.bucket("alhoe528hw2")
    blobs = bucket.list_blobs()

    link_matrix = np.zeros((20000,20000))
    progress = 0
    for blob in blobs:
        #Iterating through the files, marking each link in the linkage matrix
        progress += 1
        if progress % 100 == 0:
            print(f"Progress: {progress}/20000")
        #This method is specific to the naming convention used in this example
        link_from = int((blob.name.split('.')[0][6:]))
        with(blob.open('r')) as f:
            content = f.read()
            soup = BeautifulSoup(content, 'html.parser')
            links = soup.find_all('a')
            for link in links:
                #Find the slice containing the name of the file being linked to
                start = str(link).find('<a href=\"')
                end = str(link).find('.html\"> This is a link </a>')
                if start != -1 and end != -1:
                    link_to = int(str(link)[start+9:end])
                    link_matrix[link_from,link_to] = 1
    # Save and reload matrix from local memory for efficiency.
    np.save("link_matrix.npy", link_matrix)

link_matrix = np.load("link_matrix.npy")

incoming = np.sum(link_matrix, axis=0)
outgoing = np.sum(link_matrix, axis=1)

#Statistics computaion
print("Outgoing Mean: ", np.mean(outgoing))
print("Outgoing Median: ",np.median(outgoing))
print("Outgoing Max: ",np.max(outgoing))
print("Outgoing Min: ",np.min(outgoing))
print("Outgoing Quintiles: ", np.percentile(outgoing,[20,40,60,80]))

print("Incoming Mean: ", np.mean(incoming))
print("Incoming Median: ",np.median(incoming))
print("Incoming Max: ",np.max(incoming))
print("Incoming Min: ",np.min(incoming))
print("Incoming Quintiles: ", np.percentile(incoming,[20,40,60,80]))

print("Link Matrix:",link_matrix)

#Compute Pageranks
outgoing_no_zeros = outgoing.copy()
outgoing_no_zeros[outgoing_no_zeros == 0] = 1
sum = 0 
pageranks = np.ones(20000) / 20000
#While the sum of pageranks is more than 5% different from the previous iteration, update
while abs(pageranks.sum() - sum) > sum * 0.005:
    sum = pageranks.sum()

    pageranks = (0.85 * (link_matrix.T @ (pageranks/outgoing_no_zeros)) + (0.15 / 20000))
print("Final Pageranks: ", pageranks)
print("Total of Pageranks (should be about 1)", pageranks.sum())

#Independant Test
link_matrix = np.ones((20000,20000))
print("Complete Linkage Matrix test:",link_matrix)
outgoing = np.sum(link_matrix, axis=1)
outgoing_no_zeros = outgoing.copy()
outgoing_no_zeros[outgoing_no_zeros == 0] = 1
sum = 0 
pageranks = np.ones(20000) / 20000
#While the sum of pageranks is more than 5% different from the previous iteration, update
while abs(pageranks.sum() - sum) > sum * 0.005:
    sum = pageranks.sum()

    pageranks = (0.85 * (link_matrix.T @ (pageranks/outgoing_no_zeros)) + (0.15 / 20000))
print("Final Pageranks: (Expectation is that they are all 1/n, as all pages are equal rank) ", pageranks)
print("Total of Pageranks (should be about 1)", pageranks.sum())