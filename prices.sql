WITH NormalizedData AS (
    SELECT 
        Product_Name,
        Price,
        Link,
        -- Step 1: Standardize all pill/capsule keywords to ' CAP'
        REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(UPPER(Product_Name), 
            'CAPSULES', ' CAP'), 
            'CAPS', ' CAP'), 
            'CAP', ' CAP'), -- ensure space before CAP
            'SOFTGELS', ' CAP'), 
            'SOFTGEL', ' CAP'), 
            'TABLETS', ' CAP'), 
            'TABLET', ' CAP'), 
            'PILLS', ' CAP') AS StandardizedName
    FROM dbo.Omega
),
LeftParts AS (
    SELECT 
        Product_Name,
        Price,
        Link,
        StandardizedName,
        CHARINDEX(' CAP', StandardizedName) AS CapIndex
    FROM NormalizedData
),
ExtractedPills AS (
    SELECT 
        Product_Name,
        Price,
        Link,
        -- Step 2: Get the text to the left of ' CAP' and reverse it to extract the nearest number
        CASE 
            WHEN CapIndex > 0 THEN 
                REVERSE(LTRIM(RTRIM(SUBSTRING(StandardizedName, 1, CapIndex - 1))))
            ELSE NULL 
        END AS ReversedLeft
    FROM LeftParts
),
PillCalculation AS (
    SELECT 
        Product_Name,
        Price,
        Link,
        -- Step 3: Extract only the digits from the start of the reversed string
        TRY_CAST(
            REVERSE(
                SUBSTRING(
                    ReversedLeft, 
                    1, 
                    CASE 
                        WHEN PATINDEX('%[^0-9]%', ReversedLeft) > 0 
                        THEN PATINDEX('%[^0-9]%', ReversedLeft) - 1 
                        ELSE LEN(ReversedLeft) 
                    END
                )
            ) AS INT
        ) AS PillCount
    FROM ExtractedPills
)
-- Step 4: Run the final query with the highly accurate PillCount
SELECT 
    Product_Name,
    TRY_CAST(REPLACE(REPLACE(REPLACE(REPLACE(Price, 'EGP', ''), 'جنيه', ''), ',', ''), ' ', '') AS DECIMAL(10,2)) AS [Total Price (EGP)],
    PillCount AS [Total Pills],
    ROUND(
        (TRY_CAST(REPLACE(REPLACE(REPLACE(REPLACE(Price, 'EGP', ''), 'جنيه', ''), ',', ''), ' ', '') AS DECIMAL(10,2)) 
        / NULLIF(PillCount, 0)) * 10, 
        2
    ) AS [Price for 10 Pills (EGP)],
    Link
FROM PillCalculation
WHERE PillCount IS NOT NULL AND PillCount > 0
ORDER BY [Price for 10 Pills (EGP)] ASC;
